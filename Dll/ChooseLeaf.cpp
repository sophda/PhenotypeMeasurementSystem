#include<iostream>
#include<string>
#include <opencv2/opencv.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <pcl/PolygonMesh.h>
#include <iostream> //标准输入输出流
#include <pcl/io/pcd_io.h> //PCL的PCD格式文件的输入输出头文件
#include <pcl/point_types.h> //PCL对各种格式的点的支持头文件
#include <pcl/visualization/cloud_viewer.h>//点云查看窗口头文件
#include <fstream>
#include <pcl/point_types.h>  
#include <pcl/io/pcd_io.h>  
#include <pcl/io/ply_io.h>  
#include <pcl/io/obj_io.h>
#include <pcl/PolygonMesh.h>
#include <pcl/io/vtk_lib_io.h>
#include <pcl/kdtree/kdtree_flann.h>  
#include <pcl/features/normal_3d.h>  
#include <pcl/surface/gp3.h>  
#include <pcl/visualization/pcl_visualizer.h>  
#include <boost/thread/thread.hpp>  
#include <fstream>  
#include <iostream>  
#include <stdio.h>  
#include <string.h>  
#include <string>  
#include <vector>
#include <pcl/point_types.h>
#include <iostream>
#include <string>
//#include <unistd.h>
#include <iostream>
#include <string>
//#include <unistd.h>
#include <pcl/filters/statistical_outlier_removal.h>
#include<pcl/common/common.h>
#include <pcl/filters/passthrough.h>
// OpenCV 库
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
//#include <pcl/visualization/cloud_viewer.h>

// PCL 库
#include <pcl/io/pcd_io.h>
#include <pcl/point_types.h>

// 定义点云类型
//extern "C"
//{
//    __declspec(dllexport) float calculate_spe_area(int x, int y, int w, int h);
//}
float calculate_spe_area(int x, int y, int w, int h,int d)
{
    const double camera_factor = 1000;

    const double camera_cx = 682.3;
    const double camera_cy = 254.9;
    const double camera_fx = 979.8;  //小觅
    const double camera_fy = 942.8;
    typedef pcl::PointXYZRGBA PointT;
    typedef pcl::PointCloud<PointT> PointCloud;
    pcl::PointCloud<pcl::PointXYZRGB>::Ptr cloud(new pcl::PointCloud<pcl::PointXYZRGB>);
    pcl::io::loadPCDFile<pcl::PointXYZRGB>("D:/1/leaf.pcd", *cloud);
    int m = int(x + w / 2);
    int n = int(y + h / 2);
    cv::Mat depth;
    depth = cv::imread("d:/1/dep.png", -1);
    

    float z1 = double(d) / camera_factor;

    float x1 = (x - camera_cx) * z1 / camera_fx;
    float y1 = (y - camera_cy) * z1 / camera_fy;

    float x2 = (x + w - camera_cx) * z1 / camera_fx;
    float y2 = (y + h - camera_cy) * z1 / camera_fy;
    pcl::PointCloud<pcl::PointXYZRGB>::Ptr cloud_one(new pcl::PointCloud<pcl::PointXYZRGB>);
    cloud_one->width = cloud->width;
    cloud_one->height = cloud->height;
    cloud_one->points.resize(cloud_one->width * cloud_one->height);
    for (size_t i = 0; i < cloud->points.size(); ++i)
    {
        if ((cloud->points[i].x > x1)
            && (cloud->points[i].x < x2)
            && (cloud->points[i].y > y1)
            && (cloud->points[i].y < y2))
        {
            cloud_one->points[i].x = cloud->points[i].x;
            cloud_one->points[i].y = cloud->points[i].y;
            cloud_one->points[i].z = cloud->points[i].z;
            cloud_one->points[i].r = cloud->points[i].r;
            cloud_one->points[i].g = cloud->points[i].g;
            cloud_one->points[i].b = cloud->points[i].b;


        }
    }
    float area;
    if(cloud_one->points.size() != 0)
    { 
        pcl::io::savePCDFile("leaf_one.pcd", *cloud_one);
        area = pcl::calculatePolygonArea(*cloud_one);
    }
    else { area = -1; }

    return area;
      


}
int main()
{
    cout << calculate_spe_area(0, 0, 1024, 1024, 800) << endl;
}