import React from 'react';
import * as d3 from 'd3';
import data from './most_recent_reco.csv'

export default class Module extends React.Component {
  constructor(props) {
    super(props);
    this.state = {likes: [1,2,3],dislikes:[1,2,3],username:""};
  }

  componentDidMount(){
    let i = 0
    let self = this
    var info = d3.csv(data, function(data) {
      let newState = {...self.state}
      newState.username = data.username
      if (i < 3){
        newState.likes[i] = {img:data.image,recipe_id:data.recipe_id}
      } else {
        newState.dislikes[i-3] = {img:data.image,recipe_id:data.recipe_id}
      }
      self.setState(newState)
      i +=  1
  
  });
  }

  render() {

  console.log(this.state)
  return ( 
    <div style={{textAlign:"center"}}>
      <div style={{textAlign:"center"}}>
        <h2>Recipe Recommendations For {this.state.username}</h2>
        <p>Top 3 Recommended Recipes:</p>
      </div>

  <div class='row'>
    <div class='column'>
      <img src={this.state.likes[0].img} style={{"width":"100%"}} />
      <p>{this.state.likes[0].recipe_id}</p>
    </div>
    <div class='column'>
      <img src={this.state.likes[1].img} style={{"width":"100%"}} />
      <p>{this.state.likes[1].recipe_id}</p>
    </div>
    <div class='column'>
      <img src={this.state.likes[2].img} style={{"width":"100%"}} />
      <p>{this.state.likes[2].recipe_id}</p>
    </div>
  </div>


  <div style={{textAlign:"center", marginTop: "100px"}}>
    <p>Bottom 3 Recommended Recipes:</p>
  </div>

  <div class='row'>
    <div class='column'>
      <img src={this.state.dislikes[0].img} style={{"width":"100%"}} />
      <p>{this.state.dislikes[0].recipe_id}</p>
    </div>
    <div class='column'>
      <img src={this.state.dislikes[1].img} style={{"width":"100%"}} />
      <p>{this.state.dislikes[1].recipe_id}</p>
    </div>
    <div class='column'>
      <img src={this.state.dislikes[2].img} style={{"width":"100%"}} />
      <p>{this.state.dislikes[2].recipe_id}</p>
    </div>
  </div>

  <div class="container">
    <span onclick="this.parentElement.style.display='none'" class="closebtn">&times;</span>
    <img id="expandedImg" style={{"width":"100%"}}/>
    <div id="imgtext"></div>
  </div>
  </div>
    );
}}

