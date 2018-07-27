import React, { Component } from 'react'

import {ImageView3D} from "./gui/ImageView3D.js"
import {convertNifti, getImageData} from "./utils/images/nifti.js"
import {DropDown, RadioList} from "./utils/gui/baseComponents.js"
import {range} from "./utils/misc.js"



class App extends Component {
    
    constructor(props) {
	super(props)
	this.state = {imageIndex: -1, imageNames: [], activeMask: -1, maskVisibility: [],
		      tempWindow:1, tempLevel:0.5, window:1, level: 0.5, maskIndex: 1, 
		      brushSize:20, maskLabel:1, actionIndex:0, loading:false,
		      graphCutsText: "Start Graph Cuts"}
	this.images = []
	this.maskColours = ["#FF0000", "#FFFF00"]
	this.maskColourNames = ["Background", "Object", "Object2"]
	this.actions = ["segment","box"]
	this.specialAction = null
	this.colourBias = 0
	// Server test
	// console.log("trying")
	// var arr  = [[1,2],[3,4]]
	// var arr2 = [[5,6],[7,8]]
	// fetch("/graphCuts?image=" + JSON.stringify(arr)
	//     + "&scribbles=" + JSON.stringify(arr2)).then(function(response) {
	//     console.log(response)
	//     return response.text();
	// }).then(function(text) {
	//     console.log(text);
	// });
    }

    loadImage(file) {
	console.log("Image loading...")
	this.state.loading = true
	this.forceUpdate()
	var fr = new FileReader()
	fr.onloadend = function(evt) {
	    if (evt.target.readyState === FileReader.DONE) {
		console.log("Image loaded")
		var res = convertNifti(evt.target.result)
		var img = res[0]
		var meanVal = res[1]
		this.images.push(img)
		var imageNames = this.state.imageNames.slice(0)
		imageNames.push(file.name)
		this.specialAction = null
		this.colourBias = 0
		this.setMaskLabel(1)
		var window
		if (meanVal > 0.5) {
		    window = 2*(1 - meanVal)
		}
		else {
		    window = 2*meanVal
		}
		setTimeout( function() {
		    this.setState({imageIndex: this.images.length - 1, imageNames: imageNames,
				   activeMask: 0, maskVisibility:[true], 
				   tempWindow:window, tempLevel:meanVal,
				   window: window, level: meanVal},
				  function() {
				      this.refs.imageView.preRender()
				      this.setState({loading: false})
				  }.bind(this))
		}.bind(this), 0)
		console.log("Done")
	    }
	}.bind(this)
	var data = fr.readAsArrayBuffer(file)
    }
    
    loadMask(file) {
	console.log("mask loading")
	var fr = new FileReader()
	fr.onloadend = function(evt) {
	    if (evt.target.readyState === FileReader.DONE) {
		var imgs = getImageData(evt.target.result)[0]
		this.addNewMask()
		var currImg = this.images[this.state.imageIndex]
		for (var nImg = 0; nImg < imgs.length; nImg++) {
		    for (var y = 0; y < imgs[0].length; y++) {
			for (var x = 0; x < imgs[0][0].length; x++) {
			    currImg.setMask(nImg, y, x, imgs[nImg][y][x],
					    this.state.activeMask)
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
	this.setState({tempLevel:level})
    }
    
    setWindow(window) {
	this.setState({tempWindow:window})
    }

    levelWindowPreRender() {
	var window = parseFloat(this.state.tempWindow)
	var level  = parseFloat(this.state.tempLevel)
	if (window && level) {
	    this.state.loading = true
	    this.state.window = window
	    this.state.level = level
	    this.forceUpdate()
	    setTimeout(function() {
		this.refs.imageView.preRender()
		this.setState({loading: false})
	    }.bind(this), 0)
	}
    }

    setBrushSize(size) {
	if (size) {
	    this.setState({brushSize:size})
	}
    }

    setMaskLabel(label) {
	var maskIndex = Math.abs(label + this.colourBias)
	this.setState({maskLabel: label, maskIndex: maskIndex})
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
	console.log(maskIndex)
	var vis = this.state.maskVisibility.slice()
	vis.push(true)
	this.images[this.state.imageIndex].setActiveMask(maskIndex)
	this.setState({activeMask: maskIndex, maskVisibility: vis})
    }

    
    hideIfTrue(bool, display){
	if (bool === true) {
	    return "none"
	}
	else {
	    return display
	}
    }

    graphCuts() {
	if (this.specialAction !== 1) {
	    this.colourBias = -2
	    this.addNewMask()
	    this.specialAction = 1
	    this.setState({graphCutsText:"Confirm annotations"})
	}
	else {
	    var imgArr = []
	    var labelArr = []
	    var currImg = this.images[this.state.imageIndex]
	    for (var i = 0; i < currImg.nImages; i++) {
		imgArr.push([])
		labelArr.push([])
		for (var j = 0; j < currImg.height; j++) {
		    imgArr[i].push([])
		    labelArr[i].push([])
		    for (var k = 0; k < currImg.width; k++) {
			imgArr[i][j].push(currImg.imagesX[i].data[j][k])
			labelArr[i][j].push(currImg.imagesX[i].masks[this.state.activeMask][j][k])
		    }
		}
	    }
	    //console.log(imgArr, JSON.stringify(imgArr))
	    // imgArr = [ [ [0.1, 0.2, 0.1], [0.5, 0.5, 0.6], [0.55, 0.25, 0.1] ],
	    // 	       [ [0.1, 0.2, 0.1], [0.5, 0.5, 0.6], [0.55, 0.25, 0.1] ] ]
	    // labelArr = [ [ [2, 0, 0], [1, 0, 1], [1, 2, 0] ],
	    //  		 [ [0, 0, 0], [0, 0, 0], [0, 0, 0] ] ]
	    var url = "/graphCuts"
	    console.log("Making server request...")
	    fetch(url, {
		method: 'POST',
		headers: {
		    'Accept': 'application/json',
		    'Content-Type': 'application/json'
		},
		body: JSON.stringify({"image": JSON.stringify(imgArr),
				      "scribbles":JSON.stringify(labelArr)})
	    })
		.then(function(response) {
		    console.log(response)
		    console.log("Turning into text")
		    return response.text()
		}).then(function(text) {
		    console.log("Got text: ", text)
		    console.log(JSON.parse(text));
		});
	    console.log("Request made")
	    
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

	var currImg = this.images[this.state.imageIndex]

	console.log("RENDERING", this.state.loading)


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
		checked={this.state.imageIndex} onChange={this.changeImage.bind(this)}
		divStyleOuter={divStyle}
		radioStyle={elementStyle} labelStyle={elementStyle}
		divStyleInner={{"display":"inline-block", "width":"70%", "textAlign":"left"}}
		/>
		</div>}
	    

	    {this.state.imageIndex === -1 ? null :
	     <div style={borderStyle}>
		<p>Show/Hide Masks:</p>
		<RadioList ref="maskVisibility" options={range(0, currImg.getNumMasks())}
		exclusionary={false}
		checked={this.state.maskVisibility} onChange={this.showMasks.bind(this)}
		divStyleOuter={divStyle}
		radioStyle={elementStyle} labelStyle={elementStyle}
		divStyleInner={{"display":"inline-block", "width":"70%", "textAlign":"left"}}
		/>
		</div>}

	    {this.state.imageIndex === -1 ? null :
	     <div style={borderStyle}>
		<p>Active Mask:</p>
		<RadioList ref="activeMask" options={range(0, currImg.getNumMasks())}
		exclusionary={true}
		checked={this.state.activeMask} onChange={this.setActiveMask.bind(this)}
		divStyleOuter={divStyle}
		radioStyle={elementStyle} labelStyle={elementStyle}
		divStyleInner={{"display":"inline-block", "width":"70%", "textAlign":"left"}}
		/>
		<button onClick={(e) => {this.addNewMask(e.target.value)}}>Add New Mask</button>
		</div>}


	    <div style={borderStyle}>	    
	    <div style={divStyle}>
	    
	    <label style={labelStyle}>Level:</label>
	    <input style={inputStyle} value={this.state.tempLevel}
	    onChange={(e) => {this.setLevel(e.target.value)}}></input>
	    
	    <label style={labelStyle}>Window:</label>
	    <input style={inputStyle} value={this.state.tempWindow}
	    onChange={(e) => {this.setWindow(e.target.value)}} ></input>

	    <button onClick={this.levelWindowPreRender.bind(this)}>Apply Transform</button>
	    
	    </div>

	    <RadioList options={["Alter Mask", "Crop Image"]}
	    exclusionary={true} checked={this.state.actionIndex}
	    onChange={(val) => {this.setState({actionIndex:val})}}
	    divStyleOuter={divStyle} radioStyle={elementStyle} labelStyle={elementStyle}
	    divStyleInner={{"display":"inline-block", "width":"70%", "textAlign":"left"}}/>

	    </div>

	    
	    <div style={{"display":this.hideIfTrue(this.state.actionIndex === 1, "block")}}>
	    <div style={borderStyle}>	    
	    <div style={divStyle}>

	    <RadioList options={["Background", "Foreground"]}
	    exclusionary={true} checked={this.state.maskLabel}
	    onChange={this.setMaskLabel.bind(this)}
	    divStyleOuter={divStyle} radioStyle={elementStyle} labelStyle={elementStyle}
	    divStyleInner={{"display":"inline-block", "width":"70%", "textAlign":"left"}}/>

	    <label style={labelStyle}>Brush Size: {this.state.brushSize}</label>
	    <input style={sliderStyle} type="range"
	    min={1} max={50} defaultValue={this.state.brushSize}
	    onChange={(e) => {this.setBrushSize(parseInt(e.target.value))}}></input>

	    <button onClick={this.graphCuts.bind(this)}>{this.state.graphCutsText}</button>
	    
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
	    
	    <div style={{"display":this.hideIfTrue(this.state.loading === true, "block")}}>
	    <ImageView3D ref="imageView" image={currImg} activeMask={this.state.activeMask}
	    maskVisibility={this.state.maskVisibility} 
	    level = {this.state.level} window = {this.state.window}
	    brushSize={this.state.brushSize}
	    maskColours = {this.maskColours} maskLabel={this.state.maskIndex}
	    action={this.actions[this.state.actionIndex]}/>
	    </div>

	    <div style={{"display":this.hideIfTrue(this.state.loading === false, "block")}}>
	    Loading....
	    </div>	    
	    
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
// - Loading a picture has the final image just worse brightness? Maybe a resizing effect?

/* Memory reduction issues!
 * - Could easily turn image arrays into float32 arrays, might make some bits worse though
 */

/* Shortest term TO-DO:
 * - If background selected when doing graph cuts something weird happens
 * - Send image over + produce correct image (fix reading func.), then try a graph cuts 
 */


/*
 * Long-term TO-DO:
 * - Improve UI for going through pics with a slide bar + text box for choosing pic
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
