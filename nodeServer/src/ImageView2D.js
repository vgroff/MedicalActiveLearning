import React, { Component } from 'react'


export class ImageView2D extends Component {
    
    constructor(props) {
	super(props)
	this.state = {currImageIndex:-1, nextImageIndex:0}
	this.mouseDown = false
	this.drawingRect = false
	this.resizingRect = -1
	//this.events = {"change":this.props.onChange}
    }
    
    // Draw the image onto the canvas
    drawImage() {
	if (this.props.images.length) {
	    this.props.images[this.state.nextImageIndex].drawImage(this.refs.canvas, this.props.level, this.props.window, this.props.maskColours)
	    this.state.currImageIndex = this.state.nextImageIndex
	}
    }
    
    nextImage(dir) {
	if (this.props.images.length && this.drawingRect == false) {
	    this.props.images[this.state.currImageIndex].resetTempMask()
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
	    if (this.props.onChange) {
		this.props.onChange()
	    }
	}
    }

    handleMouseMove(x, y) {
	if (this.props.images.length) {
	    if (this.props.action==="segment") {
		this.refs.canvas.style.cursor = "default";
		var rect = this.refs.canvas.getBoundingClientRect()
		this.props.images[this.state.currImageIndex].updateTempMask(
		    x - rect.left, y - rect.top, this.props.maskLabel, this.props.brushSize)
		if (this.mouseDown === true) {
		    this.markMask()
		}
		else {
		    this.forceUpdate()
		}
	    }
	    else if (this.props.action==="box") {
		this.refs.canvas.style.cursor = "crosshair";
		var rect = this.refs.canvas.getBoundingClientRect()
		if (this.drawingRect === true) {
		    this.props.images[this.state.currImageIndex].setRectEndCoords(x - rect.left,
										  y - rect.top)
		    this.forceUpdate()
		}
		else {
		    x = x - rect.left
		    y = y - rect.top
		    var threshold = 6
		    var img = this.props.images[this.state.currImageIndex]
		    var index = -1
		    var min = threshold+1
		    if (this.resizingRect === -1) {
			if (Math.abs(x - img.boundingRect[0]) < threshold) {
			    this.refs.canvas.style.cursor = "w-resize"
			    this.resizingRect = 0
			    min = Math.abs(x - img.boundingRect[0])
			}
			else if ( (Math.abs(x - img.boundingRect[2]) < threshold) &&
				  Math.abs(x - img.boundingRect[2]) < min) {
			    this.refs.canvas.style.cursor = "e-resize"
			    this.resizingRect = 2
			}
			else if (Math.abs(y - img.boundingRect[1]) < threshold &&
				 Math.abs(y - img.boundingRect[1]) < min) {
			    this.refs.canvas.style.cursor = "n-resize"
			    this.resizingRect = 1
			}
			else if (Math.abs(y - img.boundingRect[3]) < threshold &&
				 Math.abs(y - img.boundingRect[3]) < min) {
			    this.refs.canvas.style.cursor = "s-resize"
			    this.resizingRect = 3
			}
		    }
		    // Don't resize if the mouse isn't down, and reset if so
		    if (this.mouseDown === false) {
			this.resizingRect = -1
		    }
		    if (this.resizingRect >= 0) {
			var val
			var index = this.resizingRect
			if (index % 2 == 1) {
			    val = y
			}
			else {
			    val = x
			}
			img.boundingRect[index] = val
			img.setRectCoords(img.boundingRect[0], img.boundingRect[1],
					  img.boundingRect[2], img.boundingRect[3])
			this.forceUpdate()
			if (this.props.onChange) {
			    this.props.onChange()
			}
		    }
		}
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
	    x = x - rect.left
	    y = y - rect.top
	    var img = this.props.images[this.state.currImageIndex]
	    if (this.drawingRect === false) {
		var threshold = 6
		if (Math.abs(x - img.boundingRect[0]) < threshold) {
		}
		else if (Math.abs(x - img.boundingRect[2]) < threshold) {
		}
		else if (Math.abs(y - img.boundingRect[1]) < threshold) {
		}
		else if (Math.abs(y - img.boundingRect[3]) < threshold) {
		}
		else {
		    img.setRectStartCoords(x, y)
		    img.setRectEndCoords(x, y)
		    this.drawingRect = true
		}
	    }
	    else {
		// Clicking while drawing means we stop drawing (i.e. stop updates with musoe move)
		this.drawingRect = false
	    }
	}
    }

    handleMouseOut() {
	if (this.props.images.length) {
	    if (this.props.action==="segment") {
		this.props.images[this.state.currImageIndex].resetTempMask()
		this.forceUpdate()
	    }
	    else if (this.props.action==="box") {
		if (this.drawingRect === true) {
		    this.props.images[this.state.currImageIndex].setRectEndCoords(0, 0)
		    this.props.images[this.state.currImageIndex].setRectStartCoords(0, 0)
		    this.drawingRect = false
		    this.forceUpdate()
		}
	    }
	}
	this.mouseDown = false
    }

    componentDidMount() {
	console.log("update")
	if (this.refs.canvas) {
	    this.drawImage()
	}
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
	    </div>
	)
    }
}
