import React, { Component } from 'react'

function componentToHex(c) {
    var hex = c.toString(16);
    return hex.length == 1 ? "0" + hex : hex;
}

function rgbToHex(r, g, b) {
    return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}


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
	if (this.props.images.imgDat && this.state.currImageIndex !== this.state.nextImageIndex) {
	    // If the image exists and is different than the one we are currently showing
	    // Get the dimensions
	    var height = this.props.images.imgDat[0].length
	    var width  = this.props.images.imgDat[0][0].length
	    var pixHeight = this.props.images.pixHeight
	    var pixWidth = this.props.images.pixWidth
	    // Height of the canvas is always 400
	    var size   = 200
	    // Size the canvas correctly
	    this.refs.canvas.height = size
	    this.refs.canvas.width  = size * width/height
	    // Note down the scale for later us
	    var scale = size / height
	    // Clear the canvas
	    var ctx = this.refs.canvas.getContext("2d")
	    ctx.clearRect(0, 0, width*scale, height*scale);
	    // Get the matrix representing the current image
	    var imgs = this.props.images.imgDat
	    let img = imgs[this.state.nextImageIndex]
	    //console.log("drawing", img, height)
	    for (var row = 0; row < height; row++) {
		for (var col = 0; col < width; col++) { 
		    var grayVal = parseInt(img[row][col])
		    if (grayVal >= 256) {grayVal = 255}
		    ctx.fillStyle = rgbToHex(grayVal, grayVal, grayVal); // Set the color to the one specified
		    ctx.fillRect(col * scale, row * scale * pixWidth/pixHeight, scale, scale); // Actually draw the rectangle
		    //console.log(grayVal, col * scale, row * scale, scale)
		}
	    }
	    this.state.currImageIndex = this.state.nextImageIndex
	}
    }
    
    changeImage(dir) {
	if (this.props.images.imgDat) {
	    var newImg = (this.state.currImageIndex + dir)
	    if (newImg < 0) {
		newImg = 0
	    }
	    else if (newImg >= this.props.images.imgDat.length) {
		newImg = this.props.images.imgDat.length - 1
	    }
	    this.setState({nextImageIndex : newImg})
	}
    }
    
    render() {
	this.drawImage()
	return (<div>
		<canvas ref="canvas" onWheel={(e) => {e.preventDefault(); this.changeImage(Math.abs(e.deltaY)/e.deltaY);}}/>
		</div>)
    }
}
