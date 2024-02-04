import { BellFilled, MailOutlined } from "@ant-design/icons";
import { Badge, Drawer, Image, List, Space, Typography, Avatar } from "antd";
import { useEffect, useState } from "react";
import { getComments, getOrders } from "../../API";
import { Flex } from '@tremor/react'
import { useAuth } from '../../common/AuthProvider'
import {
  UserOutlined,
} from "@ant-design/icons";
function AppHeader() {
  const [comments, setComments] = useState([]);
  const [orders, setOrders] = useState([]);
  const [commentsOpen, setCommentsOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const { user, handleLogout } = useAuth()

  const logOut = () => {
    handleLogout()
  
  }
  useEffect(() => {
    getComments().then((res) => {
      setComments(res.comments);
    });
    getOrders().then((res) => {
      setOrders(res.products);
    });
  }, []);
  return (
    <div className="AppHeader">
      {/* Left Side: Title */}
      <Typography.Title level={4} style={{ margin: 0 }}>Authr-based RAG</Typography.Title>
        
      <Space align="center" style={{ marginLeft: 'auto' }}>
        

        {/* User Icon */}
        <UserOutlined style={{ fontSize: '1.5em' }} />

        {/* Display Current User */}
        <Typography.Text strong className="ml-2">{user.sub}</Typography.Text>

        {/* Logout Button */}
        <button
          type="text"
          danger
          onClick={logOut}
          className="px-2 text-white bg-red-600 rounded-md hover:bg-red-700 active:shadow-lg"
        >
          Log Out
        </button>
      </Space>
    </div>
  );
}
export default AppHeader;
