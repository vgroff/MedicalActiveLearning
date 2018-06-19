import React, { Component } from 'react'

import {ImageView} from "./ImageView.js"
import {convertNifti} from "./utils/nifti.js"


class App extends Component {
    
    constructor(props) {
	super(props)
	this.state = {imagesX: {}, imagesY: {}, imagesZ: {}, window:2000,
		      level:1000, brushSize:1, maskLabel:1}
	this.maskColours = ["#FF0000"]
	this.maskColourNames = ["Object"]
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

    setMaskLabel(label) {
	if (label) {
	    this.setState({maskLabel: label})
	}
    }
    
    render() {
	return (
	    <div>
	    
	    <p>Select a file: <input onChange={(e) => {this.changeImage(e.target.files[0])}} type="file" id="file" name="files" /></p>
	    
	    <label>Level: </label> <input defaultValue={this.state.level} onChange={(e) => {this.setLevel(parseInt(e.target.value))}}></input>
	    
	    <label>Window: </label> <input defaultValue={this.state.window} onChange={(e) => {this.setWindow(parseInt(e.target.value))}} ></input>
	    
	    <label>
	    Scribble Label
	    </label>
	    <select style={{"appearance":"none", "MozAppearance":"none", "WebkitAppearance":"none"}}
	    defaultValue={this.state.maskLabel}>
	    <option value={0} onChange={(e) => {this.setMaskLabel(e.target.value)}} key={0}>Background</option>
	    {this.maskColours.map(function(colour, index) {
		return (
		    <option value={index+1} key={index+1} style={{"appearance":"none",
								  "MozAppearance":"none",
								  "WebkitAppearance":"none",
								  "backgroundColor":colour,
								  "color":colour
		    }}>
		    {this.maskColourNames[index]}
		    </option>
		)
	    }.bind(this))}
	    </select>
	    
	    <label>Brush Size: {this.state.brushSize}</label> <input type="range" min={1} max={50} defaultValue={this.state.brushSize} onChange={(e) => {this.setBrushSize(parseInt(e.target.value))}}></input>

	    <ImageView images = {this.state.imagesX} level = {this.state.level}
	    window = {this.state.window} brushSize={this.state.brushSize}
	    maskColours = {this.maskColours}/>

	    <ImageView images = {this.state.imagesY} level = {this.state.level}
	    window = {this.state.window} brushSize={this.state.brushSize}
	    maskColours = {this.maskColours}/>

	    <ImageView images = {this.state.imagesZ}  level = {this.state.level}
	    window = {this.state.window} brushSize={this.state.brushSize}
	    maskColours = {this.maskColours}/>
	    </div>
	)
    }
}
export default App

/*
 * TO-DO:
 * - drawing mask, brush size, representation on image etc.. different sized tools:
 * - Brush size needs to be per-pixel at least!!
 * - Add colour choices
 * - Have a "toolbar" that stays at the top of the view
 * - Need to keep the masks in-sync across different image views!!
 * - need fixes for pixel sizes if high resolution (i.e. have a minimum resolution?)
 */
