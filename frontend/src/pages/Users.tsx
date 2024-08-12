import Notification from "@/Notification";
import api from "@/utils/api";
import React from "react";
import { Link } from "react-router-dom";

type User = {
  id: number;
  name: string;
  avatar_url: string;
  username: string;
  email: string;
  total_assign: number;
  total_work: number;
};

const Users = () => {
  const [users, setUsers] = React.useState<User[]>([]);
  const [searchQuery, setSearchQuery] = React.useState<string>("");

  React.useEffect(() => {
    api
      .post("/all_users")
      .then((res) => {
        setUsers(res.data.data);
      })
      .catch((err) => {
        Notification({ message: "Problem fetching data", type: "error" });
      });
  }, []);

  const handleSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(event.target.value.toLowerCase());
  };

  const filteredUsers = users.filter(
    (user) =>
      user.name.toLowerCase().includes(searchQuery) ||
      user.username.toLowerCase().includes(searchQuery)
  );

  return (
    <>
      <div className="p-4">
        <input
          type="text"
          placeholder="Search users by name or username"
          className="p-2 w-full border rounded-md"
          onChange={handleSearch}
        />
      </div>
      <div className="p-4">
        <h1 className="text-2xl font-semibold">Users</h1>
        {filteredUsers.length > 0 ? (
          filteredUsers.map((user) => (
            <div
              key={user.id}
              className="flex justify-between items-center p-4 border-b border-gray-200 cursor-pointer hover:bg-gray-100"
            >
              <div className="flex items-center">
                <img
                  className="rounded-full h-12 w-12"
                  alt="User Avatar"
                  src={user.avatar_url}
                />
                <div className="ml-4 text-start">
                  <p className="text-lg font-semibold underline">
                    <Link to={`/user/${user.id}`}>{user.name}</Link>
                  </p>
                  <p className="text-sm text-gray-500">{user.username}</p>
                </div>
              </div>
              <div className="flex items-start">
                <p className="text-sm text-gray-500">User Id: {user.id}</p>
                <p className="text-sm text-gray-500 ml-4">
                  Total Assigned: {user.total_assign}
                </p>
                <p className="text-sm text-gray-500 ml-4">
                  Total Work: {user.total_work}
                </p>
              </div>
            </div>
          ))
        ) : (
          <p className="text-center text-gray-500">No users found</p>
        )}
      </div>
    </>
  );
};

export default Users;
