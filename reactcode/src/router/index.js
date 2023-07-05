import React from 'react';
import { createBrowserRouter } from 'react-router-dom';
import ManualAnnotate from '../pages/manualAnnotate/index'
import AutoAnnotate from '../pages/autoAnnotate/index'
import Menu from '../App'
const router = createBrowserRouter([
    {
      path: '/',
      children: [
        {
            path: '/',
            element: <Menu />
          },
        {
          path: '/annotate/auto',
          element: <AutoAnnotate />
        },
        {
          path: '/annotate/manual',
          element: <ManualAnnotate />
        },
      ]
    },
    
  ]);
  
  export default router;