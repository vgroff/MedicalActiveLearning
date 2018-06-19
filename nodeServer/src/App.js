import React, { Component } from 'react'

import {ImageView} from "./ImageView.js"
import {convertNifti} from "./utils/nifti.js"


class App extends Component {
    
    constructor(props) {
	super(props)
	this.state = {imagesX: {}, imagesY: {}, imagesZ: {}, window:2000, level:1000, brushSize:1}
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

    setBrushSize(size) {
	if (size) {
	    this.setState({brushSize:size})
	}
    }
    
    render() {
	return (
	    <div>
	    <p>Select a file: <input onChange={(e) => {this.changeImage(e.target.files[0])}} type="file" id="file" name="files" /></p>
	    <label>Level: </label> <input onChange={(e) => {this.setLevel(parseInt(e.target.value))}}></input>
	    <label>Window: </label> <input onChange={(e) => {this.setWindow(parseInt(e.target.value))}} ></input>
	    <label>Brush Size: {this.state.brushSize}</label> <input type="range" min={1} max={50} value={this.state.brushSize} onChange={(e) => {this.setBrushSize(parseInt(e.target.value))}}></input>

	    <ImageView images = {this.state.imagesX} level = {this.state.level}
	    window = {this.state.window} brushSize={this.state.brushSize}/>

	    <ImageView images = {this.state.imagesY} level = {this.state.level}
	    window = {this.state.window} brushSize={this.state.brushSize}/>

	    <ImageView images = {this.state.imagesZ}  level = {this.state.level}
	    window = {this.state.window} brushSize={this.state.brushSize}/>
	    </div>
	)
    }
}
export default App

/*
 * TO-DO:
 * - drawing mask, brush size, representation on image etc.. different sized tools:
 * - choose brush size and colour, show size of the brush - temp mask that is updated
 * - see mask versus see outline option?
 * - need fixes if high resolution
*/
