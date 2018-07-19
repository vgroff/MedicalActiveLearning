import React, { Component } from 'react'

import {ImageView3D} from "./gui/ImageView3D.js"
import {convertNifti} from "./utils/images/nifti.js"
import {DropDown, RadioList} from "./utils/gui/baseComponents.js"
import {range} from "./utils/misc.js"



class App extends Component {
    
    constructor(props) {
	super(props)
	this.state = {imageIndex: -1, imageNames: [], window:2000,
		      level:1000, brushSize:1, maskLabel:1, actionIndex:0}
	this.images = []
	this.maskColours = ["#FF0000", "#FFFF00"]
	this.maskColourNames = ["Background", "Object", "Object2"]
	this.actions = ["segment","box"]
	// Server test
	fetch("/welcome?name=RollaT").then(function(response) {
	    console.log(response)
	    return response.text();
	}).then(function(text) {
	    console.log(text);
	});
    }

    loadImage(file) {
	console.log("img loading")
	var fr = new FileReader()
	fr.onloadend = function(evt) {
	    if (evt.target.readyState === FileReader.DONE) {
		console.log("img loaded")
		var imgs = convertNifti(evt.target.result)
		console.log(imgs)
		this.images.push(imgs[3])
		var imageNames = this.state.imageNames.slice(0)
		console.log(file)
		imageNames.push(file.name)
		console.log(this.images.length)
		this.setState({imageIndex: this.images.length - 1, imageNames: imageNames})
            }
	}.bind(this)
	var data = fr.readAsArrayBuffer(file)
    }

    changeImage(index) {
	this.setState({imageIndex: index})
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
	if (parseInt(label)) {
	    this.setState({maskLabel: parseInt(label)})
	}
    }

    showMasks(masks) {
    }
    
    hideIfTrue(bool, display){
	if (bool === true) {
	    return "none"
	}
	else {
	    return display
	}
    }

    
    render() {
	var centreStyle = {"textAlign":"center"}
	var borderStyle = {"border": "2px black solid", "margin": "1px 0px 1px 0px"}
	var columnLeftStyle = Object.assign({}, {"width": "390px", "float":"left"}, centreStyle)
	var columnRightStyle = Object.assign({}, {"float":"left"}, centreStyle)
	var leftStyle = {"textAlign":"left"}
	var outerStyle = Object.assign({}, outerStyle, {"display":"inline-block","margin": "0 auto"})
	var innerStyle = Object.assign({}, outerStyle, {"display":"inline-block"})
	var divStyle = {"margin":"15px"}
	var divBorderStyle = Object.assign({}, borderStyle, divStyle)
	var elementStyle = {"margin":"0px 10px 0px 10px", "display":"inline-block"}
	var sliderStyle = Object.assign({}, elementStyle, {"display":"inline"})
	var inputStyle = Object.assign({}, elementStyle, {"width": "45px"})
	var labelStyle = Object.assign({}, elementStyle, {"margin":"0px 0px 0px 10px"})
	if (this.state.imageIndex >= 0) {
	    console.log(range(0, this.images[this.state.imageIndex].masks.length))
	}
	return (
		<div style={{"textAlign":"center"}}>
		<div style={outerStyle}>

		<div style={columnLeftStyle}>


		<div style={borderStyle}>
		<label style={labelStyle}>Select a file:</label>
		<input style={elementStyle}
	    onChange={(e) => {this.loadImage(e.target.files[0])}}
	    type="file" id="file" name="files" />
	    </div>
	    

	    <div style={{display:this.hideIfTrue(this.state.imageIndex === -1, "block")}}>

	    {this.images.length <= 1 ? null :
	     <div style={borderStyle}>
		<p>Images:</p>
		<RadioList options={this.state.imageNames} exclusionary={true}
		defaultVal={0} onChange={this.changeImage.bind(this)} divStyleOuter={divStyle}
		radioStyle={elementStyle} labelStyle={elementStyle}
		divStyleInner={{"display":"inline-block", "width":"70%", "textAlign":"left"}}
		/>
		</div>}

	    {this.state.imageIndex === -1 ? null :
	     <div style={borderStyle}>
		<p>Masks:</p>
		<RadioList options={range(0, this.images[this.state.imageIndex].masks.length)}
		exclusionary={false}
		defaultVal={0} onChange={this.showMasks.bind(this)} divStyleOuter={divStyle}
		radioStyle={elementStyle} labelStyle={elementStyle}
		divStyleInner={{"display":"inline-block", "width":"70%", "textAlign":"left"}}
		/>
		</div>}


	    <div style={borderStyle}>	    
	    <div style={divStyle}>
	    
	    <label style={labelStyle}>Level:</label>
	    <input style={inputStyle} defaultValue={this.state.level}
	    onChange={(e) => {this.setLevel(parseInt(e.target.value))}}></input>
	    
	    <label style={labelStyle}>Window:</label>
	    <input style={inputStyle} defaultValue={this.state.window}
	    onChange={(e) => {this.setWindow(parseInt(e.target.value))}} ></input>
	    
	    </div>

	    <RadioList options={["Correct Segmenetation", "Crop Image"]}
	    exclusionary={true} defaultVal={0}
	    onChange={(val) => {this.setState({actionIndex:val})}}
	    divStyleOuter={divStyle} radioStyle={elementStyle} labelStyle={elementStyle}
	    divStyleInner={{"display":"inline-block", "width":"70%", "textAlign":"left"}}/>

	    </div>

	    
	    <div style={{"display":this.hideIfTrue(this.state.actionIndex === 1, "block")}}>
	    <div style={borderStyle}>	    
	    <div style={divStyle}>

	    <DropDown label={"Scribble:"} labelStyle={labelStyle} dropDownStyle={elementStyle}
	    options={this.maskColourNames} onChange={this.setMaskLabel.bind(this)}/>

	    <label style={labelStyle}>Brush Size: {this.state.brushSize}</label>
	    <input style={sliderStyle} type="range"
	    min={1} max={50} defaultValue={this.state.brushSize}
	    onChange={(e) => {this.setBrushSize(parseInt(e.target.value))}}></input>
	    
	    </div>
	    </div>
	    </div>

	    </div> 
	    
	    </div>


	    
	    <div style={columnRightStyle}>
	    
	    <ImageView3D image={this.images[this.state.imageIndex]} level = {this.state.level}
	    window = {this.state.window} brushSize={this.state.brushSize}
	    maskColours = {this.maskColours} maskLabel={this.state.maskLabel}
	    action={this.actions[this.state.actionIndex]}/>
	    
	    </div>

	    
	    
	    </div>
	    </div>
	)
    }
}
export default App



// BUGS LIST:
// - Resize activates whenever it lines up with a side, even if not near the line - check if inside the rect first?
// - Temp mask should show on all images - they all need to be re-drawn
// - Look over cropping behaviour perhaps?

// Shortest term:
// - multiple masks UI - have 2 lists - one to show/hide, one to change which currently editing, have an add masks button. Then get them all to draw through drawImage calls and add calls to change the active mask, both will be in ImageView2D. Then fix the mask stuff so that background can be added too, only ever have 2 masks though
// - Integrate different masks into UI stuff and test it out. Remember to fix draw function to draw all masks that aren't hidden - passed in by ImageViewer.
// - Going to need a more complex UI. The standard UI and the segmentation active learning UI. Might need to split these into 2, where the seg UI is a simplified version of the standard one. In this case, I might want to have some basic building blocks of UIs, like drop-downs or lists, done separately so that they can be re-used. Drop-downs should be easy, if we want lists that can have multiple actions this may be harder work
// - Integrate a graph cuts sitch using a Gaussian for the regional term

/* Short-term TO-DO:
 * - Have multiple images and masks at once - ability to add new masks with their colour and need to index them, can also hide or show them - show mutliple at once! Load masks with each new image if allowing switching of images - FIX BACKGROUND MASK!
 * - Do a simple graph cuts with 0.5 probabilities for unmarked pixels - maybe use cropped images?
 * - Add in the CNN, try it trained as-is and then with more training
 */

/*
 * Long-term TO-DO:
 * - Dynamically calculate width required (hardcode toolbar width?)
 * - need fixes for pixel sizes if high resolution (i.e. have a minimum pic size depending on res? calculate the width dynamically instead of setting it)
 */



// Questions:
// What kind of arch? Deconvolution or dilated convolution?
// Fine-tuning?
// What datasets?
// Differently sized pixels?
// How do I use GPU server?
