import React from "react";
import { useState, useEffect } from "react";
import Notification from "../../Notification";

type Project = {
  data: Data[];
};

type Data = {
  title: string;
  username: string;
};
interface Props {
  selectedProjectId: number;
}
const AssignTaskList: React.FC<Props> = ({ selectedProjectId }) => {
  const [workData, setWorkData] = useState<Project | null>(null);
  const api = import.meta.env.VITE_API_URL;

  useEffect(() => {
    if (selectedProjectId === 0) return;
    const fetchUsers = async () => {
      try {
        const response = await fetch(api + "/assignee_task_list", {
          method: "POST",
          body: JSON.stringify({
            project_id: selectedProjectId,
          }),
          headers: {
            "Content-type": "application/json; charset=UTF-8",
          },
        });
        const data = await response.json();
        if (data.status == false) {
          Notification({ message: data.message, type: "error" });
          return;
        }

        setWorkData(data);
      } catch (error) {
        Notification({ message: "Problem fetching users", type: "error" });
      }
    };
    fetchUsers();
  }, [selectedProjectId]);
  return (
    <div className="container mx-auto p-4">
      <div style={{ height: 50 }}>
        <h1 className="text-2xl font-semibold leading-none tracking-tight">
          Assign tasks
        </h1>
      </div>

      <table className="w-full mt-4 bg-white shadow-md rounded-md overflow-hidden">
        <thead className="bg-gray-100">
          <tr>
            <th className="py-2 px-4 font-medium text-sm text-gray-700">
              Username
            </th>
            <th className="py-2 px-4 font-medium text-sm text-gray-700">
              Title
            </th>
          </tr>
        </thead>
        <tbody>
          {workData &&
            workData.data.map((project) => (
              <React.Fragment key={project.username}>
                <tr>
                  <td className="py-2 px-4">{project.username}</td>
                  <td className="py-2 px-4">{project.title}</td>
                </tr>
              </React.Fragment>
            ))}
        </tbody>
      </table>
    </div>
  );
};

export default AssignTaskList;
