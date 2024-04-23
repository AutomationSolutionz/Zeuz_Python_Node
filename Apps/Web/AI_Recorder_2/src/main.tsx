import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'
// import './assets/js/windowController.js'
// import './assets/js/panel_recorder.js'
import 'bootstrap/dist/css/bootstrap.css';
import './assets/js/panel.js'
// import { useEffect } from 'react'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)

// const script = document.createElement("script");

// script.src = "https://use.typekit.net/foobar.js";
// script.async = true;

// document.body.appendChild(script);

// useEffect(() => {
//   const script = document.createElement('script');

//   script.src = "assets/js/windowController.js";
//   script.async = true;

//   document.body.appendChild(script);

//   return () => {
//     document.body.removeChild(script);
//   }
// }, []);
// useEffect(() => {
//   const script = document.createElement('script');

//   script.src = "assets/js/panel_recorder.js";
//   script.async = true;

//   document.body.appendChild(script);

//   return () => {
//     document.body.removeChild(script);
//   }
// }, []);
// useEffect(() => {
//   const script = document.createElement('script');

//   script.src = "assets/js/panel.js";
//   script.async = true;

//   document.body.appendChild(script);

//   return () => {
//     document.body.removeChild(script);
//   }
// }, []);
