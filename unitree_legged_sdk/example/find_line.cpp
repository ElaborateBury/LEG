#include <iostream>
#include <math.h>
#include <unitree_legged_sdk/unitree_legged_sdk.h>
#include <opencv2/opencv.hpp>

#define ERROR -999

void followLine(cv::Mat frame, UNITREE_LEGGED_SDK::UnitreeLeggedSDK& robot) {
    // 转换为灰度图像
    cv::Mat gray;
    cv::cvtColor(frame, gray, cv::COLOR_BGR2GRAY);

    // 大津法二值化
    cv::Mat dst;
    cv::threshold(gray, dst, 0, 255, cv::THRESH_OTSU);

    // 膨胀，白区域变大
    cv::dilate(dst, dst, cv::Mat(), cv::Point(-1, -1), 2);

    // 获取感兴趣区域的行
    cv::Mat roi = dst.row(400);
    int blackCount = cv::countNonZero(roi == 0);

    if (blackCount >= 300) {
        // 识别到黑色十字，停止机器人运动
        robot.SpeedCommand(0, 0, 0);
        return;
    }

    if (blackCount == 0) {
        // 未观测到黑色，不执行巡线操作
        return;
    }

    // 获取黑色区域的索引
    cv::Mat blackIndex;
    cv::findNonZero(roi == 0, blackIndex);

    // 计算偏转角度
    float center = (blackIndex.at<cv::Point>(blackIndex.total() - 1).x + blackIndex.at<cv::Point>(0).x) / 2;
    float direction = center - 320;  // 320为图像中心点
    float angle = std::atan(100 / direction) * 180 / M_PI;

    // 控制机器人转向
    if (direction > 0) {
        // 偏向右侧
        int rightParam = 1999 + (direction * 4);  // 可根据实际情况调整参数
        int lightParam = 1999;
        std::string finalParam = "r:" + std::to_string(lightParam) + "l:" + std::to_string(rightParam) + "\r\n";
        // 发送串口命令
        // ...
    } else {
        // 偏向左侧
        int media = -direction;
        int lightParam = 1999 + (media * 4);
        int rightParam = 1999;
        std::string finalParam = "r:" + std::to_string(lightParam) + "l:" + std::to_string(rightParam) + "\r\n";
        // 发送串口命令
        // ...
    }
}

int main() {
    // 创建机器人对象
    UNITREE_LEGGED_SDK::UnitreeLeggedSDK robot;

    // 连接到机器人
    if (!robot.Init()) {
        std::cout << "Failed to connect to the robot!" << std::endl;
        return -1;
    }

    // 启动机器人
    robot.Start();

    // 打开摄像头
    cv::VideoCapture cap(0);
   

