import React from "react";
import api from "@/utils/api";
import { useState, useEffect } from "react";
import Notification from "../../Notification";
import "./IssueTable.css";

type Project = {
  data: Data[];
};

type Data = {
  creator_name: string;
  name: string;
  duration: number;
  issue_name: string;
  created_at: number;
  last_update: number;
};
interface Props {
  selectedProjectId: number;
  lableName: string;
}
const IssueTable: React.FC<Props> = ({ selectedProjectId, lableName }) => {
  const [issueData, setIssueData] = useState<Project | null>(null);

  const renderLabel = (props: any) => {
    const seconds = props;
    var min = null;
    var hr = null;
    var sec = null;

    hr = Math.floor(seconds / 3600);
    if (hr == 0) {
      hr = "00";
    }

    if (Number(hr) > 24) {
      const days = Math.floor(Number(hr) / 24);
      return days + " days ";
    }

    min = Math.floor((seconds % 3600) / 60);
    if (min == 0) {
      min = "00";
    }

    sec = Math.floor(seconds % 60);
    hr = hr.toString();
    if (hr.length < 2) hr = "0" + hr;

    min = min.toString();
    if (min.length < 2) min = "0" + min;

    sec = sec.toString();
    if (sec.length < 2) sec = "0" + sec;

    return `${hr}:${min}:${sec}`;
  };

  useEffect(() => {
    api
      .post("/get_issues_by_filter", {
        project_id: selectedProjectId,
        filter: lableName,
      })
      .then((response) => {
        const data = response.data;
        if (data.status == false) {
          Notification({ message: data.message, type: "error" });
          return;
        }
        setIssueData(data);
      })
      .catch((_error) => {
        Notification({
          message: "Problem While Getting Issues",
          type: "error",
        });
      });
  }, [selectedProjectId, lableName]);
  return (
    <div className="relative ">
      <table className="w-full text-sm text-left rtl:text-right text-gray-500 dark:text-gray-400">
        <thead className="text-xs text-gray-700 uppercase bg-gray-100 dark:bg-gray-700 dark:text-gray-400">
          <tr>
            <th scope="col" className="px-6 py-3 rounded-s-lg">
              Issues
            </th>
            <th scope="col" className="px-6 py-3">
              Last Event
            </th>
            <th scope="col" className="px-6 py-3 rounded-e-lg">
              Duration
            </th>
          </tr>
        </thead>
        <tbody>
          {issueData &&
            issueData.data.map((issue) => {
              return (
                <tr
                  className="bg-white dark:bg-gray-800 border-b"
                  key={issue.issue_name}
                >
                  <th
                    scope="row"
                    className="px-6 py-4  whitespace-nowrap dark:text-white cursor-default	"
                  >
                    {issue.issue_name.length > 100 ? (
                      <a
                        title={issue.issue_name}
                        className="font-medium text-gray-900 truncate"
                      >
                        {issue.issue_name}
                      </a>
                    ) : (
                      <p className="font-medium text-gray-900">
                        {issue.issue_name}
                      </p>
                    )}
                    <div>
                      created {renderLabel(issue.created_at)} ago by{" "}
                      {issue.creator_name}
                    </div>
                  </th>
                  <td className="px-10 py-4">
                    {renderLabel(issue.last_update)}
                  </td>
                  <td className="px-6 py-4">{renderLabel(issue.duration)}</td>
                </tr>
              );
            })}
        </tbody>
      </table>
    </div>
  );
};

export default IssueTable;
