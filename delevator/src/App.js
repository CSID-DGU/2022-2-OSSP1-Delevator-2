import logo from "./logo.svg";
import "./App.css";
import React, { Component } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./LoginPage";
import User from "./UserPage";
import Admin from "./AdminPage";

function App() {
  return (
    <div className="bg-[#FEFCF3] h-screen">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route
            path="/user"
            Component={() => {
              window.location.href = "https://localhost:8080";
              return null;
            }}
          />
          <Route path="/admin" element={<Admin />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
