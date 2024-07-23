import React from "react";
import { useState, useEffect } from "react";
import Notification from "../../Notification";
import api from "@/utils/api";

type Issue = {
  username: string;
  title: string;
};

type AssigneeData = {
  _id: number;
  issues: Issue[];
};

type ApiResponse = {
  status: boolean;
  data: AssigneeData[];
  message: string;
};

interface Props {
  selectedProjectId: number;
}

const AssignTaskList: React.FC<Props> = ({ selectedProjectId }) => {
  const [workData, setWorkData] = useState<Issue[]>([]);

  useEffect(() => {
    api.post("/assignee_task_list", { project_id: selectedProjectId })
      .then((response) => {
        const data: ApiResponse = response.data;
        if (data.status === false) {
          Notification({ message: data.message, type: "error" });
          return;
        }
        
        // Flatten the data
        const flattenedData: Issue[] = data.data.flatMap(assignee => assignee.issues);
        setWorkData(flattenedData);
      })
      .catch((error) => {
        Notification({ message: "Problem fetching users", type: "error" });
      });
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
          {workData.map((issue, index) => (
            <tr key={index}>
              <td className="py-2 px-4">{issue.username}</td>
              <td className="py-2 px-4">{issue.title}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AssignTaskList;
