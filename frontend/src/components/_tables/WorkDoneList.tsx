import React from "react";
import api from "@/utils/api";
import { useState, useEffect } from "react";
import Notification from "../../Notification";
import { secondsToHMSorDays } from "@/utils/timeFormate";

type Issue = {
  issue_title: string;
  total_duration: string;
};

type Project = {
  data: Data[];
};

type Data = {
  username: string;
  issues: Issue[];
  time_spend_on_project: string;
};
interface Props {
  selectedProjectId: number;
}
const UserProjectData: React.FC<Props> = ({ selectedProjectId }) => {
  const [workData, setWorkData] = useState<Project | null>(null);

  function formatData(data: any) {
    return {
      ...data,
      data: data.data.map((item: { issues: any[] }) => {
        return {
          ...item,
          issues: item.issues.map((issue) => {
            return {
              ...issue,
              total_duration: secondsToHMSorDays(issue.total_duration),
            };
          }),
        };
      }),
    };
  }
  useEffect(() => {
    api
      .post("/user_work_done_list", {
        project_id: selectedProjectId,
      })
      .then((response) => {
        const data = response.data;
        if (data.status == false) {
          Notification({ message: data.message, type: "error" });
          return;
        }
        const format_data = formatData(data);
        setWorkData(format_data);
      })
      .catch((_error) => {
        Notification({ message: "Problem fetching users", type: "error" });
      });
  }, [selectedProjectId]);
  return (
    <div className="container mx-auto p-4">
      <div style={{ height: 50 }}>
        <h1 className="text-2xl font-semibold leading-none tracking-tight">
          Work Done By users Table
        </h1>
      </div>
      <table className="w-full mt-4 bg-white shadow-md rounded-md overflow-hidden">
        <thead className="bg-gray-100">
          <tr>
            <th className="py-2 px-4 font-medium text-sm text-gray-700">
              Username
            </th>
            <th className="py-2 px-4 font-medium text-sm text-gray-700">
              Issue Title
            </th>
            <th className="py-2 px-4 font-medium text-sm text-gray-700">
              Total Duration
            </th>
          </tr>
        </thead>
        <tbody>
          {workData &&
            workData.data.map((project, index) => (
              <React.Fragment key={index}>
                {project.issues.map((issue: Issue, index: number) => (
                  <tr
                    key={index}
                    className={index % 2 === 0 ? "bg-gray-50" : "bg-white"}
                  >
                    <td className="py-2 px-4">
                      {index === 0 ? project.username : ""}
                    </td>
                    <td className="py-2 px-4">{issue.issue_title}</td>
                    <td className="py-2 px-4">{issue.total_duration}</td>
                  </tr>
                ))}
              </React.Fragment>
            ))}
        </tbody>
      </table>
    </div>
  );
};

export default UserProjectData;
