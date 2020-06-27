import React from 'react';
import logo from './logo.svg';
import './App.css';
import UCFDropzone from './components/dropzone';

function App() {
  return (
      <div className="splash">
        <div className='pegbox-logo'>
          <h1>PEGBOX</h1>
          <h2>
            Cello Optimization Software
          </h2>
        </div>
        <UCFDropzone/>
      </div>
  );
}

export default App;
