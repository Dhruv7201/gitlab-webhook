import React, { useState, useEffect } from "react";
import api from "@/utils/api";
import Notification from "@/Notification";
import { useNavigate } from "react-router-dom";
import { validateToken } from "@/utils/api";

type User = {
  id: number;
  username: string;
  name: string;
  email: string;
  level: string;
};

type Suggestion = {
  username: string;
  name: string;
  email: string;
};

const getLevel = () => {
  const jwt = localStorage.getItem("token");
  if (!jwt) return false;
  const jwtData = jwt.split(".")[1];
  const decodedJwtJsonData = window.atob(jwtData);
  const decodedJwtData = JSON.parse(decodedJwtJsonData);
  return decodedJwtData.level;
};

const UserSettings = () => {
  const navigate = useNavigate();
  useEffect(() => {
    if (localStorage.getItem("token")) {
      validateToken(localStorage.getItem("token") as string).then((res) => {
        if (!res) {
          localStorage.removeItem("token");

          navigate("/login");
        }
      });
    } else {
      navigate("/login");
    }
  }, [navigate]);
  const [users, setUsers] = useState<User[]>([]);
  const [editUser, setEditUser] = useState<User | null>(null);
  const [userSuggestions, setUserSuggestions] = useState<Suggestion[]>([]);
  const [formData, setFormData] = useState({
    username: "",
    name: "",
    password: "",
    email: "",
    level: "",
  });

  const level = getLevel();

  const fetchUsers = async () => {
    try {
      const response = await api.get("/users");
      if (response.data.status) {
        setUsers(response.data.data);
      }
    } catch (error) {
      console.error("Error fetching users:", error);
      Notification({
        type: "error",
        message: "Error fetching users",
      });
    }
  };

  // Fetch suggestions from API
  const fetchSuggestions = async () => {
    try {
      const response = await api.get("/suggestions");
      if (response.data.status) {
        setUserSuggestions(response.data.data);
      }
    } catch (error) {
      console.error("Error fetching suggestions:", error);
      Notification({
        type: "error",
        message: "Error fetching suggestions",
      });
    }
  };

  useEffect(() => {
    fetchUsers();
    fetchSuggestions();
  }, []);

  // Handle form field changes
  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // Handle form submit to add/edit user
  const handleFormSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      const response = await api.post("/login_users", formData);
      if (response.data.status) {
        Notification({
          type: "success",
          message: "User saved successfully",
        });
        fetchUsers();
        setFormData({
          username: "",
          name: "",
          password: "",
          email: "",
          level: "",
        });
        setEditUser(null);
      }
    } catch (error) {
      console.error("Error saving user:", error);
      Notification({
        type: "error",
        message: "Error saving user",
      });
    }
  };

  const handleEditClick = (user: User) => {
    setEditUser(user);
    setFormData({
      username: user.username,
      name: user.name,
      password: "",
      email: user.email,
      level: user.level,
    });
  };

  const handleDeleteClick = async (username: string) => {
    try {
      const response = await api.delete(`/login_users/${username}`);
      if (response.data.status) {
        Notification({
          type: "success",
          message: "User deleted successfully",
        });
        setUsers(users.filter((user) => user.username !== username));
      }
    } catch (error) {
      console.error("Error deleting user:", error);
      Notification({
        type: "error",
        message: "Error deleting user",
      });
    }
  };

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">User Settings</h1>

      <div className="mb-8 bg-white shadow-lg rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">
          {editUser ? "Edit User" : "Add User"}
        </h2>

        <form onSubmit={handleFormSubmit}>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            <div>
              <label className="block text-sm font-medium mb-1">Username</label>
              <input
                list="usernames"
                type="text"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                className="w-full border border-gray-300 rounded p-2"
                required
              />
              <datalist id="usernames">
                {userSuggestions.map((suggestion) => (
                  <option
                    key={suggestion.username}
                    value={suggestion.username}
                  />
                ))}
              </datalist>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Name</label>
              <input
                list="names"
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                className="w-full border border-gray-300 rounded p-2"
                required
              />
              <datalist id="names">
                {userSuggestions.map((suggestion) => (
                  <option key={suggestion.name} value={suggestion.name} />
                ))}
              </datalist>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Password</label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                className="w-full border border-gray-300 rounded p-2"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Email</label>
              <input
                list="emails"
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                className="w-full border border-gray-300 rounded p-2"
                required
              />
              <datalist id="emails">
                {userSuggestions.map((suggestion) => (
                  <option key={suggestion.email} value={suggestion.email} />
                ))}
              </datalist>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Level</label>
              <select
                name="level"
                value={formData.level}
                onChange={handleInputChange}
                className="w-full border border-gray-300 rounded p-2"
                required
              >
                <option value="" disabled>
                  Select level
                </option>
                <option value="admin">Admin</option>
                <option value="user">User</option>
              </select>
            </div>
          </div>
          <button
            type="submit"
            className="mt-4 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
          >
            {editUser ? "Update User" : "Add User"}
          </button>
          <button
            onClick={() => {
              setEditUser(null);
              setFormData({
                username: "",
                name: "",
                password: "",
                email: "",
                level: "",
              });
            }}
            className="mt-4 ml-4 bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded"
          >
            Cancel
          </button>
        </form>
      </div>

      {/* Table for viewing users */}
      <div className="bg-white shadow-lg rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Existing Users</h2>
        <table className="min-w-full bg-white">
          <thead>
            <tr>
              <th className="py-2 px-4 border-b">Username</th>
              <th className="py-2 px-4 border-b">Name</th>
              <th className="py-2 px-4 border-b">Email</th>
              <th className="py-2 px-4 border-b">Level</th>
              {level === "admin" && (
                <th className="py-2 px-4 border-b">Actions</th>
              )}
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.username}>
                <td className="py-2 px-4 border-b">{user.username}</td>
                <td className="py-2 px-4 border-b">{user.name}</td>
                <td className="py-2 px-4 border-b">{user.email}</td>
                <td className="py-2 px-4 border-b">{user.level}</td>
                {level === "admin" && (
                  <td className="py-2 px-4 border-b">
                    <button
                      onClick={() => handleEditClick(user)}
                      className="bg-yellow-500 hover:bg-yellow-700 text-white font-bold py-1 px-3 rounded mr-2"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDeleteClick(user.username)}
                      className="bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-3 rounded"
                    >
                      Delete
                    </button>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default UserSettings;
