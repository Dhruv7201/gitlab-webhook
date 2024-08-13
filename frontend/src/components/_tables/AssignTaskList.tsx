import React, { useState, useEffect } from "react";
import Notification from "../../Notification";
import api from "@/utils/api";

type TaskData = {
  task: string;
  assigned: string;
  issue_url: string;
};

type ApiResponse = {
  status: boolean;
  data: TaskData[];
  message: string;
};

interface Props {
  selectedProjectId: number;
  dateRange: any;
}

const AssignTaskList: React.FC<Props> = ({ selectedProjectId, dateRange }) => {
  const [workData, setWorkData] = useState<TaskData[]>([]);

  useEffect(() => {
    api
      .post("/assignee_task_list", { project_id: selectedProjectId })
      .then((response) => {
        const data: ApiResponse = response.data;
        if (data.status === false) {
          Notification({ message: data.message, type: "error" });
          return;
        }

        setWorkData(data.data);
      })
      .catch((error) => {
        Notification({ message: "Problem fetching users", type: "error" });
      });
  }, [selectedProjectId]);

  return (
    <div className="mt-6">
      <div>
        <h1 className="text-2xl font-semibold leading-none tracking-tight">
          Assign tasks
        </h1>
      </div>

      <table className="w-full mt-4 bg-white rounded-md overflow-hidden border border-gray-200">
        <thead className="bg-gray-100">
          <tr>
            <th className="py-2 px-4 font-medium text-sm text-gray-700">
              Task
            </th>
            <th className="py-2 px-4 font-medium text-sm text-gray-700">
              Assigned
            </th>
          </tr>
        </thead>
        <tbody>
          {workData.map((task, index) => (
            <tr
              key={index}
              className="border-b border-gray-200 hover:bg-gray-100 cursor-pointer"
            >
              <td className="py-2 px-4">
                <a
                  href={task.issue_url}
                  className="underline"
                  target="_blank"
                  rel="noreferrer"
                >
                  {task.task}
                </a>
              </td>
              <td className="py-2 px-4">{task.assigned}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AssignTaskList;
