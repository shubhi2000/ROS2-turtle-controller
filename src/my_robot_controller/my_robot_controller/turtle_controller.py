import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
from turtlesim.srv import SetPen
from functools import partial

class TurtleControllerNode(Node):

    def __init__(self):
        self.save_pos = 0
        super().__init__("turtle_controller")
        self.pose_subscriber_ = self.create_subscription(
            Pose, "/turtle1/pose", self.pose_callback, 10)
        self.cmd_vel_pub_ = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
        
    def pose_callback(self, msg: Pose):
        msg_pub_=Twist()
        if 1.5 < msg.x < 9.0 and 1.5 < msg.y < 9.0:
            msg_pub_.linear.x = 3.0
            msg_pub_.angular.z = 0.0
        else:
            msg_pub_.angular.z = 1.0
            msg_pub_.linear.x = 1.0          
             
        self.cmd_vel_pub_.publish(msg_pub_)

        if self.save_pos <= 5.5 and msg.x > 5.5:
            self.get_logger().info("Color change to green")
            self.call_set_pen_service(0,100,100,3,0)
        elif self.save_pos > 5.5 and msg.x <= 5.5:
            self.get_logger().info("Color change to purple")
            self.call_set_pen_service(100,0,100,3,0)    

        self.save_pos = msg.x

    def call_set_pen_service(self,r,g,b,width,off):
        client = self.create_client(SetPen, "/turtle1/set_pen")    
        while not client.wait_for_service(1.0):
            self.get_logger().warn("Waiting for service...")
        
        request = SetPen.Request()
        request.r = r
        request.g = g
        request.b = b
        request.width = width
        request.off = off

        future = client.call_async(request)
        future.add_done_callback(partial(self.callback_set_pen))

    def callback_set_pen(self, future):
        try:
            response = future.result()
        except Exception as e:
            self.get_logger().error("Service call failed: %r" % (e,))

def main(args=None):
    rclpy.init(args=args)
    node = TurtleControllerNode()
    rclpy.spin(node)
    rclpy.shutdown()