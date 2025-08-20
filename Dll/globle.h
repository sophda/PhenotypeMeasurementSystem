#pragma once
#include<iostream>
#include<vector>
#include<algorithm>
#include<opencv.hpp>
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/highgui/highgui.hpp"
#include <opencv2\imgproc\types_c.h>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
//#include <pcl/visualization/cloud_viewer.h>

// PCL ¿â
int g_height = 0;
int g_width = 0;

extern cv::Mat	g_marks = cv::Mat::zeros(g_height,g_width, CV_32S);
extern cv::Mat	g_src = cv::Mat::zeros(g_height, g_width, CV_8UC3);
extern cv::Mat	g_dep = cv::Mat::zeros(g_height, g_width, CV_16U);
extern cv::Mat g_pers = cv::Mat::zeros(g_height, g_width, CV_8UC3);
