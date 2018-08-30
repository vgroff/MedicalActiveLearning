import React, { Component } from 'react'

import {ImageView3D} from "./gui/ImageView3D.js"
import {convertNifti, getImageData} from "./utils/images/nifti.js"
import {DropDown, RadioList} from "./utils/gui/baseComponents.js"
import {range} from "./utils/misc.js"

async function fetchSeg(imgArr, labelArr, action, CNNName) {
    if (CNNName === undefined) {
	CNNName = 1
    }
    console.log("Making server request...")
    var res = await fetch("/segment", {
	method: 'POST',
	headers: {
	    'Accept': 'application/json',
	    'Content-Type': 'application/json',
	    "Connection": "close"
	},
	body: JSON.stringify({"image": JSON.stringify(imgArr),
			      "scribbles": JSON.stringify(labelArr),
			      "action":action, "CNNName": CNNName})
    })
    res = await res.text()
    return res
}

async function queryDatabase(action, name1, name2) {
    var body = JSON.stringify({"action":action, "name1":name1, "name2":name2})
    console.log("Making server request...")
    var res = await fetch("/query", {
	method: 'POST',
	headers: {
	    'Accept': 'application/json',
	    'Content-Type': 'application/json',
	    "Connection": "close"
	},
	body: body
    })
    res = await res.text()
    return res
}

async function trainCNN(cnnName, epochs, lr) {
    var body = JSON.stringify({"CNNName":cnnName, "epochs":epochs, "lr":lr})
    console.log("Making server request...")
    var res = await fetch("/train", {
	method: 'POST',
	headers: {
	    'Accept': 'application/json',
	    'Content-Type': 'application/json',
	    "Connection": "close"
	},
	body: body
    })
    res = await res.text()
    var blob = new Blob([res], {type:"text/plain"}) 
    var blobUrl = URL.createObjectURL(blob);
    var link = document.createElement("a"); // Or maybe get it from the current document
    link.href = blobUrl;
    link.download = "trainingLog.txt";
    var clickEvent = new MouseEvent("click", {
	"view": window,
	"bubbles": true,
	"cancelable": false
    });
    link.dispatchEvent(clickEvent)
}

async function uploadImg(cnnName, img, label) {
    var body = JSON.stringify({"CNNName":cnnName, "image":JSON.stringify(img), "label":JSON.stringify(label)})
    console.log("Making server request...")
    var res = await fetch("/upload", {
	method: 'POST',
	headers: {
	    'Accept': 'application/json',
	    'Content-Type': 'application/json',
	    "Connection": "close"
	},
	body: body
    })
    res = await res.text()
    return res
}

class App extends Component {
    
    constructor(props) {
	super(props)
	this.state = {imageIndex: -1, imageNames: [], activeMask: -1, maskVisibility: [],
		      tempWindow:1, tempLevel:0.5, window:1, level: 0.5, maskIndex: 1, 
		      brushSize:20, maskLabel:1, actionIndex:0, cnnIndex:0, newCNNAction:0, 
		      loading:false, specialAction:null, CNNName: "", nEpochs:1, lr:0.00001,
		      graphCutsText: "Graph Cuts Segmentation", maskColourIndexes:null, CNNNames:[],
		      mask1:0, mask2:0, diceScore:"", callState:""}
	this.images = []
	this.maskColours = ["#FF0000", "#FFFF00"]
	this.colours = ["#FF0000", "#0000FF", "#00FF00", "#00FFFF"]
	this.colourNames = ["Red", "Blue", "Green", "Cyan"]
	this.maskColourNames = ["Background", "Object"]
	this.actions = ["segment","box"]
	this.colourBias = 0
	this.specialMask = null
	this.truthMask = 0
	this.datasetIndex = 0
	this.getCNNs()

    }

    loadImage(file) {
	console.log("Image loading...")
	this.state.loading = true
	this.forceUpdate()
	var fr = new FileReader()
	fr.onloadend = function(evt) {
	    if (evt.target.readyState === FileReader.DONE) {
		console.log("Image loaded")
		var res = convertNifti(evt.target.result, true)
		var img = res[0]
		var meanVal = res[1]
		var maxVal = res[2]
		this.images.push(img)
		var imageNames = this.state.imageNames.slice(0)
		imageNames.push(file.name)
		this.colourBias = 0
		this.setMaskLabel(1)
		var window
		if (meanVal > maxVal/2) {
		    window = 2*(maxVal - meanVal)
		}
		else {
		    window = 2*meanVal
		}
		setTimeout( function() {
		    this.setState({imageIndex: this.images.length - 1, imageNames: imageNames,
				   activeMask: 0, maskVisibility:[true], 
				   tempWindow:window, tempLevel:meanVal,
				   window: window, level: meanVal, specialAction: null,
				   graphCutsText:"Graph Cuts Segmentation", maskColourIndexes:[0]},
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
		var imgs = getImageData(evt.target.result, true)[0]
		console.log("msk", imgs)
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
		if (this.specialMask !== null) {
		    this.setActiveMask(this.specialMask)
		}
		this.forceUpdate()
		
            }
	}.bind(this)
	var data = fr.readAsArrayBuffer(file)
    }

    getCNNs() {
	queryDatabase("allNets", "", "").then(function(cnnNames) {
	    cnnNames = JSON.parse(cnnNames)
	    this.setState({CNNNames: cnnNames})
	}.bind(this)).catch(function(e) {console.log(e)})
    }


    addNewCNN() {
	var cnnName = this.state.CNNName
	var option = "addNew"
	if (this.state.newCNNAction == 1) {
	    option = "addNewCopyData"
	}
	var res = queryDatabase(option, cnnName, this.state.CNNNames[this.state.cnnIndex]).then( function(resp) {
	    this.getCNNs()
	}.bind(this))
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

    setMaskColour(index) {
	var maskColourIndexes = this.state.maskColourIndexes.slice()
	maskColourIndexes[this.state.activeMask] = index
	this.setState({maskColourIndexes:maskColourIndexes})
    }

    setActiveMask(maskIndex) {
	if (this.state.specialAction === null) {
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
	var nColours = this.colours.length
	var maskColours = this.state.maskColourIndexes.slice()
	var colourIndex = maskColours.length % nColours
	maskColours.push(colourIndex)
	this.images[this.state.imageIndex].setActiveMask(maskIndex)
	this.setState({activeMask: maskIndex, maskVisibility: vis,
		       maskColourIndexes: maskColours})
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
	this.setState({callState: "Calling server..."})
	if (this.state.specialAction === null) {
	    this.colourBias = -2
	    this.addNewMask()
	    this.setState({specialAction:1, graphCutsText:"Confirm annotations"})
	}
	else {
	    var currImg = this.images[this.state.imageIndex]
	    var imgArr = currImg.getImgArr()
	    var labelArr = currImg.getMaskArr(this.state.activeMask)
	    var errHandle = function(err) {console.log(err)}
	    console.log("Making server request...")
	    fetch("/segment", {
		method: 'POST',
		headers: {
		    'Accept': 'application/json',
		    'Content-Type': 'application/json'
		},
		body: JSON.stringify({"image": JSON.stringify(imgArr),
				      "scribbles": JSON.stringify(labelArr),
				      "action":"graphCuts"})
	    }).then(function(response) {
		console.log("Response recieved")
		return response.text()
	    }.bind(this)).then(function(text) {
		var mask = JSON.parse(text)
		var currImg = this.images[this.state.imageIndex]
		this.addNewMask()
		currImg.copyMask(mask, currImg.imagesX[0].masks.length - 1)
		this.setState({callState: ""})
		this.forceUpdate()
	    }.bind(this)).catch(function(err) {console.log(err)});
	}
    }

    endGraphCuts() {
	if (this.state.specialAction === 1) {
	    this.colourBias = 0
	    this.setState({specialAction: null, graphCutsText:"Graph Cuts Segmentation"})
	}
    }

    cnnSeg() {
	this.setState({callState: "Calling server..."})
	if (this.state.specialAction === null) {
	    var currImg = this.images[this.state.imageIndex]
	    var imgArr = currImg.getImgArr()
	    var labelArr = currImg.getMaskArr(this.state.activeMask)
	    var cnn = this.state.CNNNames[this.state.cnnIndex]
	    console.log("Making server request...")
	    fetchSeg(imgArr, labelArr, "cnnSeg", cnn).then(function(response) {
		console.log("Response recieved")
		return response.text()
	    }.bind(this)).then(function(text) {
		console.log("text", text)
		var mask = JSON.parse(text)
		console.log("mask", mask)
		var currImg = this.images[this.state.imageIndex]
		this.addNewMask()
		currImg.copyMask(mask, currImg.imagesX[0].masks.length - 1)
		this.setState({callState: ""})
		this.forceUpdate()
	    }.bind(this)).catch(function(err) {console.log(err)});
	}
    }

    cnnGraphSeg(BIFSeg) {
	this.setState({callState: "Calling server..."})
	var cnn = this.state.CNNNames[this.state.cnnIndex]
	var currImg = this.images[this.state.imageIndex]
	var first = false
	if (this.state.specialAction === null) {
	    first = true
	    this.colourBias = -2
	    this.addNewMask()
	    this.specialMask = currImg.getNumMasks() - 1
	    this.setState({specialAction:2})
	}
	var action
	if (BIFSeg === true) {
	    action = "cnnGraphBIFSeg"
	}
	else {
	    action = "cnnGraphSeg"
	}
	var imgArr = currImg.getImgArr()
	var labelArr = currImg.getMaskArr(this.state.activeMask)
	fetchSeg(imgArr, labelArr, action, cnn).then(function(text) {
	    console.log("text", text)
	    var mask = JSON.parse(text)
	    console.log("mask", mask)
	    var currImg   = this.images[this.state.imageIndex]
	    var currMaskIndex = this.state.activeMask
	    this.addNewMask()
	    currImg.copyMask(mask, currImg.imagesX[0].masks.length - 1)
	    this.setState({activeMask: this.specialMask})
	    this.images[this.state.imageIndex].setActiveMask(this.specialMask)
	    this.setState({callState: ""})
	    this.forceUpdate()
	}.bind(this)).catch(function(err) {console.log(err)});
    }

    trainCNN() {
	trainCNN(this.state.CNNNames[this.state.cnnIndex], this.state.nEpochs, this.state.lr)
    }

    endCnnGraphSeg() {
	this.colourBias = 0
	this.setState({specialAction:null})
    }

    changeCNN(cnnIndex) {
	this.setState({cnnIndex:cnnIndex})
    }

    changeNewCNNAction(cnnActionIndex) {	
	this.setState({newCNNAction:cnnActionIndex})
    }

    setCNNName(name) {
	this.setState({CNNName: name})
    }
    
    setTruthMask(truthMaskIndex) {
	this.truthMask = truthMaskIndex
    }
    
    setNEpochs(epochs){
	if (epochs == "") {
	    this.setState({nEpochs: 0})
	}
	else if (parseInt(epochs)) {
	    this.setState({nEpochs: parseInt(epochs)})
	}
    }

    setDatasetIndex(datasetIndex) {
	this.datasetIndex = datasetIndex
    }
    
    setLr(lr) {
	if (lr == "") {
	    this.setState({lr:""})
	}
	else if (parseFloat(lr)) {
	    this.setState({lr:parseFloat(lr)})
	}
    }

    calculateDice() {
	var dice = this.images[this.state.imageIndex].calculateDice(this.state.mask1,
								    this.state.mask2)
	this.setState({diceScore:dice})
    }

    addToDatabase() {
	var currImg = this.images[this.state.imageIndex]
	var imgArr = currImg.getImgArr()
	var labelArr = currImg.getMaskArr(this.truthMask)
	var cnnName = this.state.CNNNames[this.datasetIndex]
	uploadImg(cnnName, imgArr, labelArr)
    }

    printPic() {
	var currImg = this.images[this.state.imageIndex]
	var imgArr = currImg.getImgArr()
	console.log(imgArr)
	var labelArr = currImg.getMaskArr(this.state.activeMask)
	console.log("Making server request...")
	fetch("/segment", {
	    method: 'POST',
	    headers: {
		'Accept': 'application/json',
		'Content-Type': 'application/json'
	    },
	    body: JSON.stringify({"image": JSON.stringify(imgArr),
				  "scribbles":JSON.stringify(labelArr),
				  "action": "print"})
	}).then(function(response) {
	    console.log("Response recieved")
	    return response.text()
	}.bind(this))	
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
	var divStyle2 = {"margin":"5px"}
	var divBorderStyle = Object.assign({}, borderStyle, divStyle)
	var elementStyle = {"margin":"0px 10px 0px 10px", "display":"inline-block"}
	var elementStyle2 = {"margin":"0px 5px 0px 5px", "display":"inline-block"}
	var sliderStyle = Object.assign({}, elementStyle, {"display":"inline"})
	var inputStyle = Object.assign({}, elementStyle, {"width": "45px"})
	var inputStyle2 = Object.assign({}, elementStyle, {"width": "60px"})
	var labelStyle = Object.assign({}, elementStyle, {"margin":"0px 0px 0px 10px"})

	var currImg = this.images[this.state.imageIndex]

	var colourIndexes = this.state.maskColourIndexes
	if (colourIndexes !== null) {
	    var maskColours = []
	    for (var i = 0; i < colourIndexes.length; i++) {
		maskColours.push([this.colours[colourIndexes[i]], "#FFFF00"])
	    }
	}

	
	return (
	    <div style={{"textAlign":"center"}}>
	    <div style={outerStyle}>

	    <div style={columnLeftStyle}>
	    
	    <div style={borderStyle}>
	    <p>AIs:</p>
	    <RadioList options={this.state.CNNNames} exclusionary={true}
	    checked={this.state.cnnIndex} onChange={this.changeCNN.bind(this)}
	    divStyleOuter={divStyle2}
	    radioStyle={elementStyle2} labelStyle={elementStyle2}
	    divStyleInner={{"display":"inline-block", "width":"70%", "textAlign":"left"}}
	    />
	    <div>
	    <label>Epochs:</label>
	    <input style={inputStyle} placeholder={"Epochs"}  value={this.state.nEpochs} onChange={(e) => {this.setNEpochs(e.target.value)}}></input>
	    </div>
	    <div>
	    <label>Learning Rate:</label>
	    <input style={inputStyle} placeholder={"Learning Rate"}  value={this.state.lr} onChange={(e) => {this.setLr(e.target.value)}}></input>
	    </div>
	    <button onClick={this.trainCNN.bind(this)} >Train AI</button>
	    </div>

	    <div style={borderStyle}>
	    <p>Create a new AI</p>
	    <RadioList options={["Copy selected AI", "Copy selected AI+dataset"]} exclusionary={true}
	    checked={this.state.newCNNAction} onChange={this.changeNewCNNAction.bind(this)}
	    divStyleOuter={divStyle2}
	    radioStyle={elementStyle2} labelStyle={elementStyle2}
	    divStyleInner={{"display":"inline-block", "width":"70%", "textAlign":"left"}}
	    />
	    <input style={inputStyle2} placeholder={"AI Name"}  value={this.state.CNNName} onChange={(e) => {this.setCNNName(e.target.value)}}></input>
	    <button onClick={this.addNewCNN.bind(this)}>Add New AI</button>
	    </div>

	    {this.state.callState !== "" ?
	    <div style={borderStyle}>
	    <p>{this.state.callState}</p>
	    </div> : null}
	    
	    </div>
	    
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
		<RadioList ref="maskVisibility" options={range(0, this.state.maskVisibility.length)}
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
		<RadioList ref="activeMask" options={range(0, this.state.maskVisibility.length)}
		exclusionary={true}
		checked={this.state.activeMask} onChange={this.setActiveMask.bind(this)}
		divStyleOuter={divStyle}
		radioStyle={elementStyle} labelStyle={elementStyle}
		divStyleInner={{"display":"inline-block", "width":"70%", "textAlign":"left"}}
		/>
		<DropDown options={this.colourNames} onChange={this.setMaskColour.bind(this)} />
		<button onClick={(e) => {this.addNewMask(e.target.value)}}>Add New Mask</button>
		</div>}

	    {this.state.imageIndex === -1 ? null :
	     <div style={borderStyle}>
		<DropDown label={"Truth mask"} options={range(0,this.state.maskVisibility.length)} labelStyle={elementStyle} defaultVal={0} onChange={this.setTruthMask.bind(this)} />
		<DropDown label={"Dataset"} options={this.state.CNNNames} labelStyle={elementStyle} defaultVal={0} onChange={this.setDatasetIndex.bind(this)} />
		<button onClick={this.addToDatabase.bind(this)}>Add image to dataset</button>
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

	    <RadioList options={["Segmentation", "Crop Image"]}
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

	    {this.state.specialAction === null ?
	     <button onClick={this.graphCuts.bind(this)}>{this.state.graphCutsText}</button>
			    :null}
	    {this.state.specialAction === 1 ?
	     <button onClick={this.endGraphCuts.bind(this)}>End Graph Cuts</button>
			   : null}
	    {this.state.specialAction === null ?
	     <button onClick={this.cnnSeg.bind(this)}>CNN Segmentation</button>
			   : null}
	    {this.state.specialAction === null ?
	     <button onClick={this.cnnGraphSeg.bind(this)}>CNN+Graph Cuts Segmentation</button>
			   : null}
	    {this.state.specialAction === 2 ?
	     <div>
	     <button onClick={this.cnnGraphSeg.bind(this,false)}>Add Annotations (Graph Cuts)</button>
	     <button onClick={this.cnnGraphSeg.bind(this,true)}>Add Annotations (BIFSeg)</button>
	     <button onClick={this.endCnnGraphSeg.bind(this)}>Confirm Segmentation</button>
	     </div>
			      : null}
	    
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

	    <div style={{"display":this.hideIfTrue(this.state.imageIndex === -1, "block")}}>
	    <div style={borderStyle}>
	    <DropDown label={"Mask 1"} options={range(0,this.state.maskVisibility.length)} labelStyle={elementStyle} defaultVal={0} onChange={(e) => this.setState({mask1:e})} />
	    <DropDown label={"Mask 2"} options={range(0,this.state.maskVisibility.length)} labelStyle={elementStyle} defaultVal={0} onChange={(e) => this.setState({mask2:e})} />
	    <p>{this.state.diceScore}</p>
	    <button onClick={this.calculateDice.bind(this)} >Calculate Dice</button>
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
	    maskColours = {maskColours} maskLabel={this.state.maskIndex}
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
 * - Change CNN method to copy onto correct thing. on wrong mask after graph cuts
 * - CNN+graphCuts+graphCuts annotations - does CNN+graphCuts button automatically ask? Send over and save the probs? Save on server-side?
 * - Offer multiple CNNs + active learning + active image database + eventual augmentation
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
