import React, { Component } from 'react'

import {ImageView3D} from "./gui/ImageView3D.js"
import {convertNifti} from "./utils/images/nifti.js"
import {DropDown, RadioList} from "./utils/gui/baseComponents.js"
import {range} from "./utils/misc.js"



class App extends Component {
    
    constructor(props) {
	super(props)
	this.state = {imageIndex: -1, imageNames: [], activeMask: -1, maskVisibility: [],
		      window:2000, level:1000,
		      brushSize:1, maskLabel:1, actionIndex:0}
	this.images = []
	this.maskColours = ["#FF0000", "#FFFF00"]
	this.maskColourNames = ["Background", "Object", "Object2"]
	this.actions = ["segment","box"]
	this.specialAction = null
	// Server test
	var arr = [[1,2],[3, 4]]
	fetch("/graphCuts?image=" + JSON.stringify(arr)).then(function(response) {
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
		this.images.push(imgs[3])
		var imageNames = this.state.imageNames.slice(0)
		imageNames.push(file.name)
		this.setState({imageIndex: this.images.length - 1, imageNames: imageNames,
		activeMask: 0, maskVisibility:[true]})
            }
	}.bind(this)
	var data = fr.readAsArrayBuffer(file)
    }
    
    loadMask(file) {
	console.log("mask loading")
	var fr = new FileReader()
	fr.onloadend = function(evt) {
	    if (evt.target.readyState === FileReader.DONE) {
		var imgs = convertNifti(evt.target.result)
		var imgs = imgs[0]
		this.addNewMask()
		var currImg = this.images[this.state.imageIndex]
		for (var nImg = 0; nImg < imgs.length; nImg++) {
		    for (var y = 0; y < imgs[0].data.length; y++) {
			for (var x = 0; x < imgs[0].data[0].length; x++) {
			    currImg.setMask(nImg, y, x, imgs[nImg].data[y][x],
					    this.state.activeMask)
			    //console.log("Mask", imgs[nImg].data[y][x], currImg.imagesX[nImg].masks[1][y][x])
			}
		    }
		}
		this.forceUpdate()
		
            }
	}.bind(this)
	var data = fr.readAsArrayBuffer(file)
    }

    changeImage(index) {
	this.setState({imageIndex: index})
	this.refs.imageView.resetImageIndices()
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
	if (parseInt(label) !== undefined) {
	    this.setState({maskLabel: parseInt(label)})
	}
    }

    showMasks(masks) {
	this.setState({maskVisibility: masks})
    }

    setActiveMask(maskIndex) {
	if (this.specialAction === null) {
	    this.setState({activeMask: maskIndex})
	    this.images[this.state.imageIndex].setActiveMask(maskIndex)
	}
    }

    cropImage() {
	var currImg = this.images[this.state.imageIndex]
	var newImg = currImg.cropToBoundingRect()
	this.images.push(newImg)
	var currNames = this.state.imageNames.slice()
	currNames.push(currNames[this.state.imageIndex] + " (Cropped)")
	this.refs.imageView.resetImageIndices()
	this.setState({imageIndex: currNames.length - 1, imageNames: currNames})
    }

    addNewMask() {
	var currImg = this.images[this.state.imageIndex]
	currImg.addNewMask()
	var maskIndex = currImg.getNumMasks() - 1
	var vis = this.state.maskVisibility.slice()
	vis.push(true)
	this.setState({activeMask: maskIndex,
		       maskVisibility: vis})
	this.refs.maskVisibility.setChecked(vis)
	console.log("CALL", maskIndex)
	this.refs.activeMask.onChange(maskIndex)
    }

    
    hideIfTrue(bool, display){
	if (bool === true) {
	    return "none"
	}
	else {
	    return display
	}
    }

    startGraphCuts() {
	this.addNewMask()
	this.specialAction = 1
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

	var currImg = this.images[this.state.imageIndex]

	console.log("HEY", this.images, this.state.imageIndex)


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

	    {this.state.imageIndex === -1 ? null :
	     <div style={borderStyle}>
		<label style={labelStyle}>Load mask:</label>
		<input style={elementStyle}
		onChange={(e) => {this.loadMask(e.target.files[0])}}
		type="file" id="file" name="files" />
		</div>}

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
		<p>Show/Hide Masks:</p>
		<RadioList ref="maskVisibility" options={range(0, currImg.getNumMasks())}
		exclusionary={false}
		defaultVal={[true]} onChange={this.showMasks.bind(this)} divStyleOuter={divStyle}
		radioStyle={elementStyle} labelStyle={elementStyle}
		divStyleInner={{"display":"inline-block", "width":"70%", "textAlign":"left"}}
		/>
		</div>}

	    {this.state.imageIndex === -1 ? null :
	     <div style={borderStyle}>
		<p>Active Mask:</p>
		<RadioList ref="activeMask" options={range(0, currImg.getNumMasks())}
		exclusionary={true}
		defaultVal={0} onChange={this.setActiveMask.bind(this)} divStyleOuter={divStyle}
		radioStyle={elementStyle} labelStyle={elementStyle}
		divStyleInner={{"display":"inline-block", "width":"70%", "textAlign":"left"}}
		/>
		<button onClick={(e) => {this.addNewMask(e.target.value)}}>Add New Mask</button>
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

	    <RadioList options={["Alter Mask", "Crop Image"]}
	    exclusionary={true} defaultVal={0}
	    onChange={(val) => {this.setState({actionIndex:val})}}
	    divStyleOuter={divStyle} radioStyle={elementStyle} labelStyle={elementStyle}
	    divStyleInner={{"display":"inline-block", "width":"70%", "textAlign":"left"}}/>

	    </div>

	    
	    <div style={{"display":this.hideIfTrue(this.state.actionIndex === 1, "block")}}>
	    <div style={borderStyle}>	    
	    <div style={divStyle}>

	    <RadioList options={["Background", "Foreground"]}
	    exclusionary={true} defaultVal={1}
	    onChange={this.setMaskLabel.bind(this)}
	    divStyleOuter={divStyle} radioStyle={elementStyle} labelStyle={elementStyle}
	    divStyleInner={{"display":"inline-block", "width":"70%", "textAlign":"left"}}/>

	    <label style={labelStyle}>Brush Size: {this.state.brushSize}</label>
	    <input style={sliderStyle} type="range"
	    min={1} max={50} defaultValue={this.state.brushSize}
	    onChange={(e) => {this.setBrushSize(parseInt(e.target.value))}}></input>

	    <button onClick={this.startGraphCuts.bind(this)}>Graph Cuts</button>
	    
	    </div>
	    </div>
	    </div>


	    <div style={{"display":this.hideIfTrue(this.state.actionIndex === 0, "block")}}>
	    <div style={borderStyle}>	    
	    <div style={divStyle}>

	    <button onClick={this.cropImage.bind(this)}>Crop Image</button>
	    
	    </div>
	    </div>
	    </div>
	    

	    </div> 
	    
	    </div>


	    
	    <div style={columnRightStyle}>
	    
	    <ImageView3D ref="imageView" image={currImg} activeMask={this.state.activeMask}
	    maskVisibility={this.state.maskVisibility} 
	    level = {this.state.level} window = {this.state.window}
	    brushSize={this.state.brushSize}
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

/* Shortest term TO-DO:
 * - Might want to get Python to draw out a cropped image to be used
 * - Create a new mask and somehow hard-code it in as the mask that needs to be chosen - reject changes? Might need to do the radio list correctly instead (pass in "checked" (maskVis) as a prop?). Add a "bias" to mask index that is only 1 during graph cuts to shift the colours around (or abs(-2) in order to keep the foreground colour the same?)
 * - Pass this mask and the current image to the server
 */

/* Short-term TO-DO:
 * - Do a simple graph cuts with 0.5 probabilities for unmarked pixels - maybe use cropped images?
 * - Add in the CNN, try it trained as-is and then with more training
 */

/*
 * Long-term TO-DO:
 * - Dynamically calculate width required (hardcode toolbar width?)
 * - need fixes for pixel sizes if high resolution (i.e. have a minimum pic size depending on res? calculate the width dynamically instead of setting it)
 * - Change the radio lists so that checked is a prop and onChange at the list level calls an onChange with the new checked array
 */



// Questions:
// What kind of arch? Deconvolution or dilated convolution?
// Fine-tuning?
// What datasets?
// Differently sized pixels?
// How do I use GPU server?
