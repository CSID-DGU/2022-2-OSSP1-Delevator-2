// import "./LoginPage.css";
import { Link, useNavigate } from "react-router-dom";
import { React, Component } from "react";

// function inputValueChange() {
//   var inputValue = document.getElementsByClassName("input").value;
//   var userLogin = document.getElementsById("userLogin");
//   userLogin.setattribute("href", "http://localhost:8080/user/" + inputValue);
//   console.log(inputValue);
// }

export class LoginPage extends Component {
  state = {
    inputValue: "",
  };

  inputValueChange = (e) => {
    this.setState({ inputValue: e.target.value });
    console.log(this.state.inputValue);
  };
  // const navigate = useNavigate();
  render() {
    return (
      <div className="relative h-screen mx-60 mb-12 ">
        <div className="text-center text-slate-700 font-sans py-6">
          <b className="uppercase text-3xl antialiased">Delevator</b>
          </div>
        <div className="box-border border-2 border-gray-100
        backdrop-saturate-50 shadow-inner drop-shadow-md
        flex h-4/5 p-4 
        justify-center rounded-md">
          <div className="m-auto">
            <form id="username">
              <div className="transition duration-150 ease-in-out 
              bg-gradient-to-r from-amber-100 to-yellow-100
              box-border border-2 border-gray-400 
              w-auto my-6 rounded-2xl shadow-inner hover:scale-105 hover:opacity-70">
                <a
                  id="userLogin"
                  target="_blank"
                  href={"http://localhost:8080/user/" + this.state.inputValue}
                >
                  <div className="my-4 mx-12 ">
                    <div className="borderline-div" />
                      <b className="text-xl mx-12">사용자 로그인</b>
                    </div>
                </a>
              </div>

              <div className="">
                <input
                  className="justify-center box-border border-4 
                  text-center 
                  shadow-inner
                  border-gray-100
                  w-auto h-auto my-6 mx-16 rounded-lg"
                  type="text"
                  placeholder="Enter User ID"
                  onChange={this.inputValueChange}
                />
              </div>

              {/* <div className="flex justify-center">
                <div className="or-div">OR</div>
              </div>
              <div className="line2"></div>
              <div className="line1"></div> */}

              <div className="transition duration-150 ease-in-out 
              bg-gradient-to-r from-cyan-100 to-sky-200
              box-border border-2 border-gray-400 
              w-auto my-6 rounded-2xl 
              shadow-inner hover:scale-105 hover:opacity-70">
                <Link to="/admin">
                  <div className="div8">
                    <div className="my-4 mx-12">
                      <div className="borderline-div" />
                      <b className="text-xl mx-12">관리자 로그인</b>
                    </div>
                  </div>
                </Link>
              </div>
        
              
              
            </form>
          </div>
        </div>
      </div>
    );
  }
}

export default LoginPage;
