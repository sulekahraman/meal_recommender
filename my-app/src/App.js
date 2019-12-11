import React from 'react';
import logo from './logo.svg';
import './App.css';
import Module from './Module'

function myFunction(imgs) {
  var expandImg = document.getElementById("expandedImg");
  var imgText = document.getElementById("imgtext");
  expandImg.src = imgs.src;
  imgText.innerHTML = imgs.alt;
  expandImg.parentElement.style.display = "block";
}
function App() {
  return (<Module/>);
}

export default App;
