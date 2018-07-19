import React, { Component } from 'react'


export class ImageView extends Component {
    
    constructor(props) {
	super(props)
	this.state = {currImageIndex:-1, nextImageIndex:0}
	this.mouseDown = false
	this.drawingRect = false
    }
    
    componentDidMount() {
    }

    // Draw the image onto the canvas
    drawImage() {
	if (this.props.images.length) {
	    this.props.images[this.state.nextImageIndex].drawImage(this.refs.canvas, this.props.level, this.props.window, this.props.maskColours)
	    this.state.currImageIndex = this.state.nextImageIndex
	}
    }
    
    nextImage(dir) {
	if (this.props.images.length) {
	    var newImg = (this.state.currImageIndex + dir)
	    if (newImg < 0) {
		newImg = 0
	    }
	    else if (newImg >= this.props.images.length) {
		newImg = this.props.images.length - 1
	    }
	    this.setState({nextImageIndex : newImg})
	}
    }

    markMask() {
	if (this.props.images.length) {
	    var rect = this.refs.canvas.getBoundingClientRect()
	    this.props.images[this.state.currImageIndex].addToMask()
	    this.forceUpdate()
	}
    }

    handleMouseMove(x, y) {
	if (this.props.images.length) {
	    if (this.props.action==="segment") {
		var rect = this.refs.canvas.getBoundingClientRect()
		this.props.images[this.state.currImageIndex].updateTempMask(
		    x - rect.left, y - rect.top, this.props.maskLabel, this.props.brushSize)
		if (this.mouseDown === true) {
		    this.markMask()
		}
		this.forceUpdate()
	    }
	    else if (this.props.action==="box" && this.drawingRect === true) {
		var rect = this.refs.canvas.getBoundingClientRect()
		this.props.images[this.state.currImageIndex].setRectEndCoords(x - rect.left,
									      y - rect.top)
		this.forceUpdate()
	    }
	}
    }

    handleMouseDown(x, y) {
	this.mouseDown = true
	if (this.props.action==="segment") {
	    this.markMask(x,y)
	}
	else if (this.props.action==="box") {
	    var rect = this.refs.canvas.getBoundingClientRect()
	    this.props.images[this.state.currImageIndex].setRectEndCoords(x - rect.left,
									  y - rect.top)
	    if (this.drawingRect === false) {
		this.props.images[this.state.currImageIndex].setRectStartCoords(x - rect.left,
										y - rect.top)
		this.drawingRect = true
	    }
	    else {
		this.drawingRect = false
	    }
	}
    }

    handleMouseOut() {
	if (this.props.images.length) {
	    if (this.props.action==="segment") {
		this.props.images[this.state.currImageIndex].updateTempMask(0,0,
									    this.props.maskLabel,0)
		this.forceUpdate()
	    }
	    else if (this.props.action==="box") {
		if (this.drawRect === true) {
		    this.props.images[this.state.currImageIndex].setRectEndCoords(0, 0)
		    this.props.images[this.state.currImageIndex].setRectStartCoords(0, 0)
		    this.drawingRect = false
		    this.forceUpdate()
		}
	    }
	}
	this.mouseDown = false
    }
    
    render() {
	if (this.refs.canvas) {
	    this.drawImage()
	}
	return (
	    <div>
	    <canvas ref="canvas"
	    onWheel={(e) => {e.preventDefault(); this.nextImage(Math.abs(e.deltaY)/e.deltaY);}}
	    onMouseMove={(e) => {this.handleMouseMove(e.clientX, e.clientY)}}
	    onMouseDown={(e) => {this.handleMouseDown(e.clientX, e.clientY)}}
	    onMouseUp={(e) => {this.mouseDown = false}}
	    onMouseOut={(e) => {this.handleMouseOut()}}/>
	    </div>)
    }
}
