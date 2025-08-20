#include<iostream>
#include<vector>
#include"globle.h"
#include<string>
#include<algorithm>
#include<opencv.hpp>
#include <pcl/io/pcd_io.h>  
#include <pcl/io/ply_io.h>  
#include <pcl/io/obj_io.h>
#include <opencv2/opencv.hpp>
#include <pcl/PolygonMesh.h>
#include <pcl/io/vtk_lib_io.h>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <pcl/kdtree/kdtree_flann.h>  
#include <opencv2\imgproc\types_c.h>
#include <opencv2/core/core.hpp>
#include <pcl/common/common.h>
#include <pcl/filters/statistical_outlier_removal.h>
#include <pcl/features/normal_3d.h>  
#include <pcl/surface/gp3.h>  
#include <boost/thread/thread.hpp>  
#include <pcl/point_types.h>

using namespace std;
extern "C"
{
	__declspec(dllexport) float ret_area(int x, int y,int meank, float thresh, int height, int width);
	__declspec(dllexport) void filter_water(unsigned char* rgb_s,
								unsigned char* dep_s,
								unsigned char *weighted, int height, int width);
}
class point
{
public:
	int x, y;
	float d;

};
template<typename T> 
class filter
{
public:
	int X,Y;
	int jiange;
	point p1, p2, p3, p4, p5, p6, p7, p8;
	double mse2;
	filter(int x1, int y1, T D1, T D2, T D3, T D4, T D5, T D6, T D7, T D8)
		: X{x1},Y{y1}
	{
		double average = (D1 + D2 + D3 + D4 + D5 + D6 + D7 + D8)/8;
		mse2 =
			(D1 - average) * (D1 - average) +
			(D2 - average) * (D2 - average) +
			(D3 - average) * (D3 - average) +
			(D4 - average) * (D4 - average) +
			(D5 - average) * (D5 - average) +
			(D6 - average) * (D6 - average) +
			(D7 - average) * (D7 - average) +
			(D8 - average) * (D8 - average);

		//p1.d = D1;
		//p2.d = D2;
		//p3.d = D3;
		//p4.d = D4;
		//p5.d = D5;
		//p6.d = D6;
		//p7.d = D7;
		//p8.d = D8;
		set_nearpoint();

	}
	~filter()
	{
	}
	void set_nearpoint()
	{
		int num = 1;
		int plx = X, ply = Y;
		p1.x = plx + num;
		p1.y = ply + num;

		p2.x = plx - num;
		p2.y = ply - num;

		p3.x = plx + num;


		p4.y = ply + num;

		p5.x = plx + num;
		p5.y = ply - num;

		p6.x = plx - num;
		p6.y = ply + num;


		p7.y = ply - num;

		p8.x = plx - num;


	}
};

bool sortfun(filter<float> &p1,filter<float> &p2)
{
	return p1.mse2 >  p2.mse2;
}


cv::Vec3b RandomColor(int value) //< span style = "line-height: 20.8px; font-family: sans-serif;" >//生成随机颜色函数</span>  
{	

		value = value % 255;  //生成0~255的随机数  
		cv::RNG rng;
		int aa = rng.uniform(0, value);
		int bb = rng.uniform(0, value);
		int cc = rng.uniform(0, value);
		return cv::Vec3b(aa,bb,cc);
	

}


void filter_water(unsigned char* rgb_s,
	unsigned char* dep_s, 
	unsigned char* weighted,
	int height,
	int width)
{
	g_height = height;
	g_width = width;

	int jiange = 1; float delete_rate = 0.56; 
	cv::Mat gray,canny_img;
	
	cv::Mat src=cv::Mat::zeros(height, width, CV_8UC3);
	//src.setTo(0);
	//cv::Mat src_img = cv::imread("D:/1/rgb.jpg",-1);
	cv::Mat src_img(height,width,CV_8UC3,rgb_s);
	//cv::Mat dep = cv::imread("D:/1/dep.png",-1);
	cv::Mat dep(height, width, CV_16U, dep_s);
	for (int i = 256; i < 769; i++)
	{
		for (int j = 256; j < 769; j++)
		{
			src.ptr<cv::Vec3b>(i)[j] = src_img.ptr<cv::Vec3b>(i)[j];
		}
	}
	g_src = src;  //保存进全局变量
	g_dep = dep;
	cv::cvtColor(src, gray, CV_BGR2GRAY);

	cv::Canny(gray,canny_img,42,218);
	int num = 0;
	vector<filter<float>> queue;
	for (int i = 256; i < 769; i++)
	{
		for (int j = 256; j < 769; j++)
		{
			if (canny_img.at<uchar>(i, j) == 255)
			{
				queue.emplace_back(i,j,
					dep.ptr<ushort>(i+jiange)[j+jiange],
					dep.ptr<ushort>(i-jiange)[ j-jiange],
					dep.ptr<ushort>(i+jiange)[ j],
					dep.ptr<ushort>(i)[j+jiange],
					dep.ptr<ushort>(i+jiange)[ j-jiange],
					dep.ptr<ushort>(i-jiange)[ j+jiange],
					dep.ptr<ushort>(i)[j-jiange],
					dep.ptr<ushort>(i-jiange)[j]);
				
			}
		}
	}
	sort(queue.begin(), queue.end(), sortfun);
	//cout << queue.size() << endl;
	//cout << queue.size()*delete_rate<<endl;
	int delete_pointnum = queue.size() * delete_rate;
	for (int i = 0; i<delete_pointnum; i++)
	{
		queue.pop_back();
	}
	//cout << queue.size();

	cv::Mat after_filter = cv::Mat::zeros(height,width,CV_8UC1);
	//after_filter.setTo(0);
	for (vector<filter<float>>::iterator it = queue.begin(); it != queue.end(); it++)
	{	
		after_filter.ptr<uchar>(it->X)[it->Y] = 255;

	}
	//cv::Mat Gaussianimg = eliminate_noise(after_filter);
	//cout << Gaussianimg.size();


		//查找轮廓  
	vector<vector<cv::Point>> contours;
	vector<cv::Vec4i> hierarchy;
	cv::findContours(after_filter, contours, hierarchy, cv::RETR_TREE, cv::CHAIN_APPROX_SIMPLE, cv::Point());
	cv::Mat imageContours = cv::Mat::zeros(after_filter.size(), CV_8UC1);  //轮廓     
	cv::Mat marks(after_filter.size(), CV_32S);   //Opencv分水岭第二个矩阵参数  
	marks = cv::Scalar::all(0);
	int index = 0;
	int compCount = 0;
	for (; index >= 0; index = hierarchy[index][0], compCount++)
	{
		cv::drawContours(marks, contours, index, cv::Scalar::all(compCount + 1), 1, 8, hierarchy);
		cv::drawContours(imageContours, contours, index, cv::Scalar(255), 1, 8, hierarchy);
	}

	cv::Mat marksShows;
	cv::convertScaleAbs(marks, marksShows);
	//imshow("marksShow", marksShows);
	//imshow("轮廓", imageContours);
	cv::watershed(src, marks);

	cv::Mat afterWatershed;
	cv::convertScaleAbs(marks, afterWatershed);

	//imshow("After Watershed", afterWatershed);
	cv::Mat PerspectiveImage = cv::Mat::zeros(after_filter.size(), CV_8UC3);
	for (int i = 0; i < marks.rows; i++)
	{
		for (int j = 0; j < marks.cols; j++)
		{
			int index = marks.at<int>(i, j);
			
			if (marks.at<int>(i, j) == -1)
			{
				PerspectiveImage.at<cv::Vec3b>(i, j) = cv::Vec3b(255, 255, 255);
			}
			else
			{
				PerspectiveImage.at<cv::Vec3b>(i, j) = RandomColor(index);
			}
		}
	}
	//imshow("After ColorFill", PerspectiveImage);
	cv::imwrite("cache/pers.jpg", PerspectiveImage);
	g_marks = marks;
	

	g_pers = PerspectiveImage;
	//分割并填充颜色的结果跟原始图像融合  
	cv::Mat wshed;
	cv::addWeighted(src, 0.4, PerspectiveImage, 0.6, 0, wshed);
	memcpy(weighted,wshed.data,height*width*3);
	//cv::imshow("AddWeighted Image", wshed);
	cv::imwrite("cache/wei.jpg", wshed);
	//cout<<ret_area(512,512);
	//cv::waitKey();
	//imshow("", after_filter);
	//hough_circle(after_filter);
	//imshow("a", after_filter);





}

float ret_area(int x, int y,int meank,float thresh, int height, int width)
{
	const double camera_cx = 682.3;
	const double camera_cy = 254.9;
	const double camera_fx = 979.8;  //小觅
	const double camera_fy = 942.8;


	pcl::PointCloud<pcl::PointXYZRGBA>::Ptr cloud(new pcl::PointCloud<pcl::PointXYZRGBA>);

	//int index_one = g_marks.at<int>(x,y);
	cv::Vec3b c_index = g_pers.at<cv::Vec3b>(y,x);
	//cout << x<<" y "<<y<<" "<<c_index << endl;
	//cv::Mat img_one = cv::Mat::zeros(1024, 1024, CV_8UC3);
	cv::Mat img_one(height, width, CV_8UC3);
	for (int i = 256; i < 749; i++)
	{
		for (int j = 256 ; j < 749; j++)
		{
			if (g_pers.at<cv::Vec3b>(i, j) == c_index)
			{
				//out.ptr<cv::Vec3b>(i)[j] = g_src.ptr<cv::Vec3b>(i)[j];
				img_one.ptr<cv::Vec3b>(i)[j] = g_src.ptr<cv::Vec3b>(i)[j];
				ushort d = g_dep.ptr<ushort>(i)[j];
				// d 可能没有值，若如此，跳过此点
				if (d == 0 || d >= 4096)
					continue;

				//获得一个点的位置与颜色
				// d 存在值，则向点云增加一个点
				pcl::PointXYZRGBA p;
				// 计算这个点的空间坐标
				p.z = double(d) / 1000;
				p.x = (j - camera_cx) * p.z / camera_fx;
				p.y = (i - camera_cy) * p.z / camera_fy;
				// 从rgb图像中获取它的颜色
				// rgb是三通道的BGR格式图，所以按下面的顺序获取颜色
				p.b = g_src.ptr<uchar>(i)[j * 3];
				p.g = g_src.ptr<uchar>(i)[j * 3 + 1];
				p.r = g_src.ptr<uchar>(i)[j * 3 + 2];

				// 把p加入到点云中
				cloud->points.push_back(p);
			}
		}
	}
	
	//cv::Mat out(1024,1024,CV_8UC3);
	//for (int i = 256; i < 749; i++)
	//{
	//	for (int j = 256; j < 749; j++)
	//	{
	//		if (g_marks.at<int>(i, j) == index_one)
	//		{
	//			out.ptr<cv::Vec3b>(i)[j] = g_src.ptr<cv::Vec3b>(i)[j];
	//		}
	//	}
	//}
	cv::imwrite("cache/out.jpg", img_one);
	cloud->height = 1;
	cloud->width = cloud->points.size();
	cloud->is_dense = false;
	pcl::PointCloud<pcl::PointXYZRGBA>::Ptr cloud_after_sta(new pcl::PointCloud<pcl::PointXYZRGBA>);

	pcl::StatisticalOutlierRemoval<pcl::PointXYZRGBA> sor;
	sor.setInputCloud(cloud);
	sor.setMeanK(meank);
	sor.setStddevMulThresh(thresh);
	sor.filter(*cloud_after_sta);
	//sor.setNegative(true);
	float area = pcl::calculatePolygonArea(*cloud_after_sta);



	pcl::io::savePCDFile("cache/leaf_one.pcd", *cloud_after_sta);


	return area ;
}
