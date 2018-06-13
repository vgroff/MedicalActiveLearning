import React, { Component } from 'react'


export class ImageView extends Component {
    
    constructor(props) {
	super(props)
	this.state = {currImageIndex:-1, nextImageIndex:0}
    }
    
    componentDidMount() {
	console.log("mounted")
    }

    // Draw the image onto the canvas
    drawImage() {
	if (this.props.images.length) {
	    this.props.images[this.state.nextImageIndex].drawImage(this.refs.canvas, this.props.level, this.props.window)
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

    markPixel(x, y) {
	var rect = this.refs.canvas.getBoundingClientRect()
	this.props.images[this.state.nextImageIndex].addToMask(x - rect.left, y - rect.top, 1)
	this.forceUpdate()
    }
    
    render() {
	this.drawImage()
	return (
	    <div>
	    <canvas ref="canvas"
	    onWheel={(e) => {e.preventDefault(); this.nextImage(Math.abs(e.deltaY)/e.deltaY);}} 
	    onClick={(e) => {this.markPixel(e.clientX, e.clientY)}}/>
	    </div>)
    }
}
