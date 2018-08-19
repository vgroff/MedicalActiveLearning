#include "gridCut3D.h"
#include <cmath>
#include <iostream>



float expWeight(double diff, double dist, double sigma) {
	return std::exp(-(diff)*diff/(2*sigma*sigma))/dist;
}

std::vector< std::vector< std::vector < double > > > gridCut3D(std::vector< std::vector< std::vector < double > > > image,
							       std::vector< std::vector< std::vector< std::vector < double > > > > regTerms,
							       double edgeCoeff, double sigma) {
	// Import Grid, create grid
	int depth = image.size();
	int height = image[0].size();
	int width = image[0][0].size();
	Grid3D grid = new GridGraph_3D_26C<double, double, float>(depth, height, width);
	int xyDir[4][2]  = { {0,1}, {1,1}, {1,0}, {1,-1} } ;

	std::vector<std::vector<std::vector <double> > > counts;
	for (int z = 0; z < depth; z++) {
		std::vector<std::vector <double> > img;
		for (int y=0;y<height;y++) {
			std::vector <double> row;
			for (int x=0;x<width;x++) {
				row.push_back(grid->get_segment(grid->node_id(z,y,x)));
			}
			img.push_back(row);
		}
		counts.push_back(img);
	}

	for (int z = 0; z < depth; z++) {
		for (int y=0;y<height;y++) {
			for (int x=0;x<width;x++) {
				grid->set_terminal_cap(grid->node_id(z, y, x), regTerms[0][z][y][x],
						       regTerms[1][z][y][x]);
				// Grid set edge
				for (int  i = - 1; i <= 1; i++) {
					for (int j = 0; j < 4; j++) {
						int newZ = z + i;
						int newX = x + xyDir[j][1];
						int newY = y + xyDir[j][0];
						if (newX >= 0 and newX <= width - 1 and newY >= 0
						    and newY <= height - 1 and newZ >= 0
						    and newZ <= depth - 1) {
							counts[z][y][x] += 1;
							counts[newZ][newY][newX] += 1;
							float distSq = pow(newZ - z, 2)
								+ pow(newY - y, 2)
								+ pow(newX - x, 2);
							float dist = pow(distSq, 0.5);
							float weight = edgeCoeff*expWeight(image[z][y][x]-image[newZ][newY][newX], dist, sigma);
							grid->set_neighbor_cap(grid->node_id(z, y, x),
									       i, xyDir[j][0],
									       xyDir[j][1], weight);
						}
					}
				}
				if (z < depth - 1 and z >= 0) {
					counts[z][y][x] += 1;
					counts[z+1][y][x] += 1;
					float weight = expWeight(image[z][y][x]-image[z+1][y][x], 1, sigma);
					grid->set_neighbor_cap(grid->node_id(z,y,x), +1, 0, 0, weight);
				}
			}
		}
	}

	grid->compute_maxflow();

	std::vector<std::vector<std::vector <double> > > segmentation;
	for (int z = 0; z < depth; z++) {
		std::vector<std::vector <double> > img;
		for (int y=0;y<height;y++) {
			std::vector <double> row;
			for (int x=0;x<width;x++) {
				row.push_back(grid->get_segment(grid->node_id(z,y,x)));
			}
			img.push_back(row);
		}
		segmentation.push_back(img);
	}
	delete grid;
	return segmentation;
 }
