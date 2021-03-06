import React, { Component } from 'react'

function disableBodyScroll() {
    var body = document.getElementsByTagName('body')[0]
    body.style.overflowY = 'hidden'
}
function enableBodyScroll() {
    var body = document.getElementsByTagName('body')[0]
    body.style.overflowY = 'auto'
}

// Displays a 2D image and interacts with the underlying image object
export class ImageView2D extends Component {
    
    constructor(props) {
	super(props)
	this.state = {currImageIndex:-1, nextImageIndex:0}
	this.mouseDown = false
	this.drawingRect = false
	this.resizingRect = -1
	this.height = 400
	//this.events = {"change":this.props.onChange}
    }
    
    // Draw the image onto the canvas
    drawImage() {
	if (this.props.images.length) {
	    this.props.images[this.state.nextImageIndex].drawImage(this.refs.canvas,
								   this.height,
								   this.props.level,
								   this.props.window,
								   this.props.maskVisibility,
								   this.props.maskColours)
	    this.state.currImageIndex = this.state.nextImageIndex
	}
    }

    preRenderImages() {
	for (var i = 0; i < this.props.images.length; i++) {
	    this.props.images[i].preRenderImage(this.height, this.props.level, this.props.window)
	}
    }

    setImageIndex(index) {
	this.setState({nextImageIndex: index})
    }

    // Switch to the next or previous image 
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

    // Turn the temporary mask into a permanent one
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

    // Move the mask or bounding box depending on whats happening
    handleMouseMove(x, y) {
	if (this.props.images.length) {
	    if (this.props.action==="segment") {
		this.refs.canvas.style.cursor = "default";
		var rect = this.refs.canvas.getBoundingClientRect()
		this.props.images[this.state.currImageIndex].updateTempMask(
		    x - rect.left, y - rect.top, this.props.maskLabel, this.props.brushSize)
		if (this.mouseDown === true) {
		    // Keep adding to the mask if mouse is down
		    this.markMask()
		}
		else {
		    // Otherwise just update
		    this.forceUpdate()
		}
	    }
	    else if (this.props.action==="box") {
		this.refs.canvas.style.cursor = "crosshair";
		var rect = this.refs.canvas.getBoundingClientRect()
		if (this.drawingRect === true) {
		    // If drawing the rectangle, move the end coordinate
		    this.props.images[this.state.currImageIndex].setRectEndCoords(x - rect.left,
										  y - rect.top)
		    this.forceUpdate()
		}
		else {
		    // If resizing, find which side to resize and then change the rect
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

    // Handle a mouse click
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

    // Reset things when the mouse leaves the canvas
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
	enableBodyScroll()
    }

    onScroll(e) {
	e.preventDefault();
	if (Math.abs(e.deltaY) > 0) {
	    this.nextImage(Math.abs(e.deltaY)/e.deltaY);
	}
    }

    handleMouseOver(e) {
	disableBodyScroll()
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
	    <div onWheel={this.onScroll.bind(this)}>
	    <canvas ref="canvas"
	    onMouseMove={(e) => {this.handleMouseMove(e.clientX, e.clientY)}}
	    onMouseDown={(e) => {this.handleMouseDown(e.clientX, e.clientY)}}
	    onMouseUp={(e) => {this.mouseDown = false}}
	    onMouseOut={(e) => {this.handleMouseOut()}}
	    onMouseOver={(e) => {this.handleMouseOver()}}/>
	    </div>
	)
    }
}
