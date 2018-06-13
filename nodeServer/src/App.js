import React, { Component } from 'react'

import {ImageView} from "./ImageView.js"
import {convertNifti} from "./utils/nifti.js"


class App extends Component {
    
    constructor(props) {
	super(props)
	this.state = {imagesX: {}, imagesY: {}, imagesZ: {}, window:2000, level:1000}
    }

    changeImage(file) {
	console.log("img changed")
	var fr = new FileReader()
	fr.onloadend = function(evt) {
	    console.log("img loaded")
	    if (evt.target.readyState === FileReader.DONE) {
                var imgs = convertNifti(evt.target.result)
		console.log("img converted")
		this.setState({imagesX : imgs[0], imagesY : imgs[1], imagesZ : imgs[2]})
            }
	}.bind(this)
	var data = fr.readAsArrayBuffer(file)
    }

    setLevel(level) {
	if (level) {
	    this.setState({level:level})
	}
    }
    
    setWindow(window) {
	if (window) {
	    this.setState({window:window})
	}
    }
    
    render() {
	return (<div>
	    <p>Hello</p>
	    <p>Select a file: <input onChange={(e) => {this.changeImage(e.target.files[0])}} type="file" id="file" name="files" /></p>
	    <label>Level: </label> <input onChange={(e) => {this.setLevel(parseInt(e.target.value))}}></input>
	    <label>Window: </label> <input onChange={(e) => {this.setWindow(parseInt(e.target.value))}} ></input>
	    <ImageView images = {this.state.imagesX} level = {this.state.level} window = {this.state.window}/>
	    <ImageView images = {this.state.imagesY} level = {this.state.level} window = {this.state.window}/>
	    <ImageView images = {this.state.imagesZ}  level = {this.state.level} window = {this.state.window}/>
	    </div>
	)
    }
}
export default App

/*
 * Order:
 * - Display all 3
 * - Consider how to deal with scaling issues - we have voxel dims that we can normalize to 1, and maybe what we return is an array of objects for each x,y,z with imgDat and pixel height/width
 * - Having image scrolling
 * TO-DO:
 * - drawing mask, brush size, representation on image etc.. different sized tools
*/
