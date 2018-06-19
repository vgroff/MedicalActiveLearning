import React, { Component } from 'react'


export class ImageView extends Component {
    
    constructor(props) {
	super(props)
	this.state = {currImageIndex:-1, nextImageIndex:0}
	this.mouseDown = false
    }
    
    componentDidMount() {
	console.log("mounted")
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
	    var rect = this.refs.canvas.getBoundingClientRect()
	    this.props.images[this.state.currImageIndex].updateTempMask(x - rect.left, y - rect.top, 1, this.props.brushSize)
	    if (this.mouseDown === true) {
		this.markMask()
	    }
	    this.forceUpdate()
	}
    }

    handleMouseDown(x, y) {
	this.mouseDown = true
	this.markMask(x,y)
    }

    handleMouseOut() {
	if (this.props.images.length) {
	    this.props.images[this.state.currImageIndex].updateTempMask(0,0,1,0)
	    this.forceUpdate()
	}
    }
    
    render() {
	this.drawImage()
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
