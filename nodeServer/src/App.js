import React, { Component } from 'react'

import {ImageView} from "./ImageView.js"
import {convertNifti} from "./utils/nifti.js"


class App extends Component {
    
    constructor(props) {
	super(props)
	this.state = {imagesX: {}, imagesY: {}, imagesZ: {}, window:2000,
		      level:1000, brushSize:1, maskLabel:1, actionIndex:0}
	this.maskColours = ["#FF0000", "#FFFF00"]
	this.maskColourNames = ["Object", "Object2"]
	this.actions = ["segment","box"]
    }

    changeImage(file) {
	console.log("img changed")
	var fr = new FileReader()
	fr.onloadend = function(evt) {
	    console.log("img loaded")
	    if (evt.target.readyState === FileReader.DONE) {
                var imgs = convertNifti(evt.target.result)
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
	this.setState({maskLabel: label})
    }
    
    render() {
	var outerStyle = {"textAlign":"center"}
	var toolbarStyle = Object.assign({}, outerStyle, {"position":"fixed", 
							  "left":"0", "right":"0",
							  "margin":"auto",
							  "backgroundColor":"white"}) 
	var divStyle = {"margin":"15px"}
	var elementStyle = {"margin":"0px 10px 0px 10px", "display":"inline-block"}
	var inputStyle = Object.assign({}, elementStyle, {"width": "45px"})
	var labelStyle = Object.assign({}, elementStyle, {"margin":"0px 0px 0px 10px"})


	return (
	    <div style={outerStyle}>

	    <div style={toolbarStyle}>
	    
	    <label style={labelStyle}>Select a file:</label>
	    <input style={elementStyle}
	    onChange={(e) => {this.changeImage(e.target.files[0])}}
	    type="file" id="file" name="files" />


	    
	    <div style={divStyle}>
	    
	    <label style={labelStyle}>Level:</label>
	    <input style={inputStyle} defaultValue={this.state.level}
	    onChange={(e) => {this.setLevel(parseInt(e.target.value))}}></input>
	    
	    <label style={labelStyle}>Window:</label>
	    <input style={inputStyle} defaultValue={this.state.window}
	    onChange={(e) => {this.setWindow(parseInt(e.target.value))}} ></input>
	    
	    </div>



	    <div style={divStyle}>

	    <p style={elementStyle}>Correct Segmentation</p>
	    <input name="actionIndex" style={elementStyle} type="radio"
	    value={0} onChange={(e) => {this.setState({actionIndex:0})}}
	    checked={this.state.actionIndex===0 ? "checked" : false}></input>
	    <p style={elementStyle}>Bounding Box</p>
	    <input name="actionIndex" style={elementStyle} type="radio"
	    value={1} onChange={(e) => {this.setState({actionIndex:1})}}
	    checked={this.state.actionIndex===1 ? "checked" : false}></input>
	    
	    </div>

	    
	    
	    <div style={divStyle}>
	    
	    <label style={labelStyle}> Scribble Label:</label>
	    <select style={elementStyle}
	    onChange={(e) => {this.setMaskLabel(parseInt(e.target.value))}}
	    defaultValue={this.state.maskLabel}>

	    <option value={0} key={0}>Background</option>
	    {this.maskColours.map(function(colour, index) {
		return (
		    <option value={index+1} key={index+1} style={{"backgroundColor":colour,
								  "color":colour}}>
		    {this.maskColourNames[index]}
		    </option>
		)
	    }.bind(this))}

	    </select>

	    <label style={labelStyle}>Brush Size: {this.state.brushSize}</label>
	    <input style={elementStyle} type="range"
	    min={1} max={50} defaultValue={this.state.brushSize}
	    onChange={(e) => {this.setBrushSize(parseInt(e.target.value))}}></input>
	    
	    </div>

	    <div>
	    </div>

	    </div>
	    
	    <ImageView images = {this.state.imagesX} level = {this.state.level}
	    window = {this.state.window} brushSize={this.state.brushSize}
	    maskColours = {this.maskColours} maskLabel={this.state.maskLabel}
	    action={this.actions[this.state.actionIndex]}/>

	    <ImageView images = {this.state.imagesY} level = {this.state.level}
	    window = {this.state.window} brushSize={this.state.brushSize}
	    maskColours = {this.maskColours} maskLabel={this.state.maskLabel}
	    action={this.actions[this.state.actionIndex]}/>

	    <ImageView images = {this.state.imagesZ} level = {this.state.level}
	    window = {this.state.window} brushSize={this.state.brushSize}
	    maskColours = {this.maskColours} maskLabel={this.state.maskLabel}
	    action={this.actions[this.state.actionIndex]}/>

	    
	    
	    </div>
	)
    }
}
export default App

// Have a 3D image viewer which keeps the 3 2D image viewers in-sync?
// Put the image toolbar on the left
// Bootstrap styling

/*
 * TO-DO:
 * - Need to keep the masks in-sync across different image views!!
 * - Allow 2D images (i.e. change image viewer)
 * - Communication with node server
 * - need fixes for pixel sizes if high resolution (i.e. have a minimum pic size depending on res?)
 */
