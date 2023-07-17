import torch
import torch.distributed
import torch.nn.functional as F

"""Adapted from https://github.dev/microsoft/Semi-supervised-learning/tree/main/semilearn/algorithms/freematch"""

def replace_inf_to_zero(val):
    val[val == float('inf')] = 0.0
    return val

def entropy_loss(mask, logits_s, prob_model, label_hist):
    mask = mask.bool()

    # select samples
    logits_s = logits_s[mask]

    prob_s = logits_s.softmax(dim=-1)
    _, pred_label_s = torch.max(prob_s, dim=-1)

    hist_s = torch.bincount(pred_label_s, minlength=logits_s.shape[1]).to(logits_s.dtype)
    hist_s = hist_s / hist_s.sum()

    # modulate prob model 
    prob_model = prob_model.reshape(1, -1)
    label_hist = label_hist.reshape(1, -1)
    # prob_model_scaler = torch.nan_to_num(1 / label_hist, nan=0.0, posinf=0.0, neginf=0.0).detach()
    prob_model_scaler = replace_inf_to_zero(1 / label_hist).detach()
    mod_prob_model = prob_model * prob_model_scaler
    mod_prob_model = mod_prob_model / mod_prob_model.sum(dim=-1, keepdim=True)

    # modulate mean prob
    mean_prob_scaler_s = replace_inf_to_zero(1 / hist_s).detach()
    # mean_prob_scaler_s = torch.nan_to_num(1 / hist_s, nan=0.0, posinf=0.0, neginf=0.0).detach()
    mod_mean_prob_s = prob_s.mean(dim=0, keepdim=True) * mean_prob_scaler_s
    mod_mean_prob_s = mod_mean_prob_s / mod_mean_prob_s.sum(dim=-1, keepdim=True)

    loss = mod_prob_model * torch.log(mod_mean_prob_s + 1e-12)
    loss = loss.sum(dim=1)
    return loss.mean(), hist_s.mean()


def ce_loss(logits, targets, reduction='none'):
    """
    cross entropy loss in pytorch.

    Args:
        logits: logit values, shape=[Batch size, # of classes]
        targets: integer or vector, shape=[Batch size] or [Batch size, # of classes]
        # use_hard_labels: If True, targets have [Batch size] shape with int values. If False, the target is vector (default True)
        reduction: the reduction argument
    """
    if logits.shape == targets.shape:
        # one-hot target
        log_pred = F.log_softmax(logits, dim=-1)
        nll_loss = torch.sum(-targets * log_pred, dim=1)
        if reduction == 'none':
            return nll_loss
        else:
            return nll_loss.mean()
    else:
        log_pred = F.log_softmax(logits, dim=-1)
        targets = targets.long()
        return F.nll_loss(log_pred, targets, reduction=reduction)




def consistency_loss(logits, targets, name='ce', mask=None):
    """
    consistency regularization loss in semi-supervised learning.

    Args:
        logits: logit to calculate the loss on and back-propagation, usually being the strong-augmented unlabeled samples
        targets: pseudo-labels (either hard label or soft label)
        name: use cross-entropy ('ce') or mean-squared-error ('mse') to calculate loss
        mask: masks to mask-out samples when calculating the loss, usually being used as confidence-masking-out
    """

    assert name in ['ce', 'mse']
    # logits_w = logits_w.detach()
    if name == 'mse':
        probs = torch.softmax(logits, dim=-1)
        loss = F.mse_loss(probs, targets, reduction='none').mean(dim=1)
    else:
        loss = ce_loss(logits, targets, reduction='none')

    if mask is not None:
        # mask must not be boolean type
        loss = loss * mask

    return loss.mean()





@torch.no_grad()
def concat_all_gather(tensor):
    """
    Performs all_gather operation on the provided tensors.
    *** Warning ***: torch.distributed.all_gather has no gradient.
    """
    tensors_gather = [torch.ones_like(tensor)
        for _ in range(torch.distributed.get_world_size())]
    torch.distributed.all_gather(tensors_gather, tensor)

    output = torch.cat(tensors_gather, dim=0)
    return output


class FreeMatchThresholingHook:
    """
    SAT in FreeMatch
    """
    def __init__(self, num_classes=2, momentum=0.999, *args, **kwargs):
        self.num_classes = num_classes
        self.m = momentum
        
        self.p_model = torch.ones((self.num_classes)) / self.num_classes
        self.label_hist = torch.ones((self.num_classes)) / self.num_classes
        self.time_p = self.p_model.mean()
    
    @torch.no_grad()
    def update(self, algorithm, probs_x_ulb):
        max_probs, max_idx = torch.max(probs_x_ulb, dim=-1,keepdim=True)

        self.time_p = self.time_p * self.m + (1 - self.m) * max_probs.mean()
        
        if algorithm.clip_thresh:
            self.time_p = torch.clip(self.time_p, 0.0, 0.95)

        self.p_model = self.p_model * self.m + (1 - self.m) * probs_x_ulb.mean(dim=0)
        hist = torch.bincount(max_idx.reshape(-1), minlength=self.p_model.shape[0]).to(self.p_model.dtype) 
        self.label_hist = self.label_hist * self.m + (1 - self.m) * (hist / hist.sum())

        algorithm.p_model = self.p_model 
        algorithm.label_hist = self.label_hist 
        algorithm.time_p = self.time_p 
    

    @torch.no_grad()
    def masking(self, algorithm, logits_x_ulb, softmax_x_ulb=True, *args, **kwargs):
        if not self.p_model.is_cuda:
            self.p_model = self.p_model.to(logits_x_ulb.device)
        if not self.label_hist.is_cuda:
            self.label_hist = self.label_hist.to(logits_x_ulb.device)
        if not self.time_p.is_cuda:
            self.time_p = self.time_p.to(logits_x_ulb.device)

        if softmax_x_ulb:
            probs_x_ulb = torch.softmax(logits_x_ulb.detach(), dim=-1)
        else:
            # logits is already probs
            probs_x_ulb = logits_x_ulb.detach()

        self.update(algorithm, probs_x_ulb)

        max_probs, max_idx = probs_x_ulb.max(dim=-1)
        mod = self.p_model / torch.max(self.p_model, dim=-1)[0]
        mask = max_probs.ge(self.time_p * mod[max_idx]).to(max_probs.dtype)
        return mask

def smooth_targets(logits, targets, smoothing=0.1):
    """
    label smoothing
    """
    with torch.no_grad():
        true_dist = torch.zeros_like(logits)
        true_dist.fill_(smoothing / (logits.shape[-1] - 1))
        true_dist.scatter_(1, targets.data.unsqueeze(1), (1 - smoothing))
    return true_dist



class PseudoLabelingHook:
    """
    Pseudo Labeling Hook
    """
    @torch.no_grad()
    def gen_ulb_targets(self, 
                        algorithm, 
                        logits, 
                        use_hard_label=True, 
                        T=1.0,
                        softmax=True, # whether to compute softmax for logits, input must be logits
                        label_smoothing=0.0):
        
        """
        generate pseudo-labels from logits/probs

        Args:
            algorithm: base algorithm
            logits: logits (or probs, need to set softmax to False)
            use_hard_label: flag of using hard labels instead of soft labels
            T: temperature parameters
            softmax: flag of using softmax on logits
            label_smoothing: label_smoothing parameter
        """

        logits = logits.detach()
        if use_hard_label:
            # return hard label directly
            pseudo_label = torch.argmax(logits, dim=-1)
            if label_smoothing:
                pseudo_label = smooth_targets(logits, pseudo_label, label_smoothing)
            return pseudo_label
        
        # return soft label
        if softmax:
            # pseudo_label = torch.softmax(logits / T, dim=-1)
            pseudo_label = algorithm.compute_prob(logits / T)
        else:
            # inputs logits converted to probabilities already
            pseudo_label = logits
        return pseudo_label
        
        
class USBAlgorithm:
    T = 0.5
    use_hard_label = True
    lambda_u = 1.0  # ulb_loss_ratio
    lambda_e = 0.001  # ent_loss_ratio
    clip_thresh = True


    def process_out_dict(self, out_dict=None, **kwargs):
        """
        process the out_dict as return of train_step
        """
        if out_dict is None:
            out_dict = {}

        for arg, var in kwargs.items():
            out_dict[arg] = var
        
        # process res_dict, add output from res_dict to out_dict if necessary
        return out_dict


    def process_log_dict(self, log_dict=None, prefix='train', **kwargs):
        """
        process the tb_dict as return of train_step
        """
        if log_dict is None:
            log_dict = {}

        for arg, var in kwargs.items():
            log_dict[f'{prefix}/' + arg] = var
        return log_dict


# call after each train_step to update parameters
def update_weights(loss, optimizer, scheduler):
    loss.backward()
    optimizer.step()
    if scheduler:
        scheduler.step()
    optimizer.zero_grad()
    return optimizer, scheduler



def train_step(predictor, optimizer, scheduler, x_lb, y_lb, x_ulb_w, x_ulb_s, criterion, exp_avg):
    num_lb = y_lb.shape[0]
    outs_x_lb = predictor(x_lb) 
    logits_x_lb = outs_x_lb
    outs_x_ulb_s = predictor(x_ulb_s)
    logits_x_ulb_s = outs_x_ulb_s
    with torch.no_grad():
        outs_x_ulb_w = predictor(x_ulb_w)
        logits_x_ulb_w = outs_x_ulb_w
    
    # logits have shape (B, 1) because we predict the score of positive class
    # now we transform logits to (B, 2) for cross entropy loss
    logits_x_lb = torch.cat([-logits_x_lb, logits_x_lb], dim=-1)
    logits_x_ulb_s = torch.cat([-logits_x_ulb_s, logits_x_ulb_s], dim=-1)
    logits_x_ulb_w = torch.cat([-logits_x_ulb_w, logits_x_ulb_w], dim=-1)

    sup_loss = ce_loss(logits_x_lb, y_lb, reduction='mean')

    mask = freematch_thresholding.masking(algorithm, logits_x_ulb_s, softmax_x_ulb=False)

    pseudo_label = pseudo_labeling.gen_ulb_targets(algorithm=algorithm,
                                          logits=logits_x_ulb_w,
                                          use_hard_label=algorithm.use_hard_label,
                                          T=algorithm.T)


    # calculate unlabeled loss
    unsup_loss = consistency_loss(logits_x_ulb_s,
                                    pseudo_label,
                                    'ce',
                                    mask=mask)
    
    # calculate entropy loss
    if mask.sum() > 0:
        ent_loss, _ = entropy_loss(mask, logits_x_ulb_s, algorithm.p_model, algorithm.label_hist)
    else:
        ent_loss = 0.0
    # ent_loss = 0.0
    total_loss = sup_loss + algorithm.lambda_u * unsup_loss + algorithm.lambda_e * ent_loss

    log_dict = algorithm.process_log_dict(sup_loss=sup_loss.item(), 
                                        unsup_loss=unsup_loss.item(), 
                                        total_loss=total_loss.item(), 
                                        util_ratio=mask.float().mean().item())
    optimizer, scheduler = update_weights(total_loss, optimizer, scheduler)
    return predictor, optimizer, scheduler, log_dict


freematch_thresholding = FreeMatchThresholingHook()
pseudo_labeling = PseudoLabelingHook()
algorithm = USBAlgorithm()





def get_weak_and_strong_augmentations(img):
    return img, img