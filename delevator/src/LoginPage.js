import "./LoginPage.css";
import { Link } from "react-router-dom";
import React from "react";

const toAdmin = () => {
  document.location.href("/admin");
};
const toUser = () => {
  document.location.href("/user");
};

const LoginPage = () => {
  return (
    <div className="login-page-div">
      <Link to="/user">
        <div className="div7">
          <div className="searchbargroup-div">
            <div className="borderline-div" />
            <b className="b5">사용자 로그인</b>
          </div>
        </div>
      </Link>
      <Link to="/admin">
        <div className="div8">
          <div className="searchbargroup-div">
            <div className="borderline-div" />
            <b className="b5">관리자 로그인</b>
          </div>
        </div>
      </Link>
      <div className="site-name-div2">
        <b className="delevator-b">Delevator</b>
      </div>
      <input className="input" type="text" placeholder="Enter User ID" />
      <div className="div9">
        <div className="or-div">OR</div>
      </div>
      <div className="line2"></div>
      <div className="line1"></div>
    </div>
  );
};

export default LoginPage;
