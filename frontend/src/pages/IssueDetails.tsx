import React, { useEffect, useState } from "react";
import api from "@/utils/api";
import { useParams } from "react-router-dom";
import IssueComponent from "@/components/_ui/IssueComponent";
import IssueFooter from "@/components/_ui/IssueFooter";
import { Copy, ExternalLink } from "lucide-react";
import Notification from "@/Notification";

const IssueDetails = () => {
  const { issueId } = useParams();
  const currIssueId = Number(issueId);
  const [issueInfo, setIssueInfo] = useState<any>(null);

  useEffect(() => {
    api
      .post("/get_issues_info", {
        issue_id: currIssueId,
      })
      .then((response) => {
        console.log(response.data);
        setIssueInfo(response.data);
      });
  }, [currIssueId]);

  const copyToClipboard = (text: string) => {
    const el = document.createElement("textarea");
    el.value = text;
    document.body.appendChild(el);
    el.select();
    document.execCommand("copy");
    document.body.removeChild(el);
    Notification({ message: "Copied to clipboard", type: "success" });
  };

  const exportIssueDetails = (issueId: number) => {
    // get file response from server
    api
      .post("/export_issue_details", {
        issue_id: issueId,
      })
      .then((response) => {
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", `issue-${issueId}.json`);
        document.body.appendChild(link);
        link.click();
      })
      .catch((_error) => {
        Notification({ message: "Problem exporting data", type: "error" });
      });
  };

  return (
    <>
      {issueInfo && (
        <div className="p-4">
          <div className="mb-4 flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <h1 className="text-2xl font-semibold leading-none tracking-tight">
                Issue Details
              </h1>
              <span className="text-sm text-gray-500">
                (Issue ID: {currIssueId})
              </span>
              <Copy
                size={16}
                className="cursor-pointer"
                onClick={() => {
                  copyToClipboard(currIssueId.toString());
                }}
              />
            </div>
            <button
              className="mt-2 text-sm text-blue-500 cursor-pointer focus:outline-none"
              onClick={() => {
                exportIssueDetails(currIssueId);
              }}
            >
              Export issue details
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="table-auto w-full text-left">
              <tbody>
                <tr className="bg-gray-100">
                  <td className="px-4 py-2 font-medium">Name</td>
                  <td className="px-4 py-2">{issueInfo.data[0].name}</td>
                </tr>
                <tr>
                  <td className="px-4 py-2 font-medium">Issue URL</td>
                  <td className="px-4 py-2">
                    <a
                      className="text-blue-500"
                      href={issueInfo.data[0].url}
                      target="_blank"
                      rel="noreferrer"
                    >
                      {issueInfo.data[0].url}
                      <ExternalLink size={16} className="inline-block ml-1" />
                    </a>
                  </td>
                </tr>
                <tr className="bg-gray-100">
                  <td className="px-4 py-2 font-medium">Project URL</td>
                  <td className="px-4 py-2">
                    <a
                      className="text-blue-500"
                      href={issueInfo.data[0].project_url}
                      target="_blank"
                      rel="noreferrer"
                    >
                      {issueInfo.data[0].project_url}
                      <ExternalLink size={16} className="inline-block ml-1" />
                    </a>
                  </td>
                </tr>
                <tr>
                  <td className="px-4 py-2 font-medium">Project Name</td>
                  <td className="px-4 py-2">
                    {issueInfo.data[0].project_name}
                  </td>
                </tr>
                <tr className="bg-gray-100">
                  <td className="px-4 py-2 font-medium">Created At</td>
                  <td className="px-4 py-2">
                    {issueInfo.data[0].created_at.replace("T", " ")}
                  </td>
                </tr>
                <tr>
                  <td className="px-4 py-2 font-medium">Re-Open Count</td>
                  <td className="px-4 py-2">
                    {issueInfo.data[0].reopen_count === undefined ||
                    issueInfo.data[0].reopen_count === null
                      ? 0
                      : issueInfo.data[0].reopen_count}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div className="mt-8">
            <div className="mb-4">
              <IssueComponent selectedIssueId={currIssueId} />
            </div>
            <div>
              <IssueFooter selectedIssueId={currIssueId} />
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default IssueDetails;
