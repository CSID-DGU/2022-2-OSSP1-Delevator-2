import "./LoginPage.css";
import { Link, useNavigate } from "react-router-dom";
import React from "react";

const LoginPage = () => {
  const navigate = useNavigate();
  return (
    <div className="login-page-div">
      <a target={"_blank"} href="http://localhost:8080/">
        <div className="div7">
          <div className="searchbargroup-div">
            <div className="borderline-div" />
            <b className="b5">사용자 로그인</b>
          </div>
        </div>
      </a>
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
