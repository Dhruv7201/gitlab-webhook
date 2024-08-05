import React from "react";
import api from "@/utils/api";
import { useState, useEffect } from "react";
import Notification from "../../Notification";

type issuesObject = {
  _id: string;
  count: number;
};

const percentage = (issues: issuesObject[]): number => {
  const closed = issues
    .filter(issue => issue._id === 'closed')
    .reduce((acc, issue) => acc + issue.count, 0);
  const all_issues = issues.reduce((acc: number, issue) => acc + issue.count, 0);
  if (all_issues === 0) return 0;
  return (closed * 100) / all_issues;
};

type milestoneObject = {
  title: string;
  start_date: string;
  due_date: string;
  web_url: string;
  id: number;
  issues: issuesObject[] | null;
};

interface Props {
  selectedProjectId: number;
  selectedOption: string;
}

const MileStoneTable: React.FC<Props> = ({ selectedProjectId, selectedOption }) => {
  const [milestoneArr, setMilestoneArr] = useState<milestoneObject[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(20);
  useEffect(() => {
    api
      .post("/milestones", {
        project_id: selectedProjectId,
      })
      .then((response) => {
        const data = response.data;
        console.log("---------", data.data);
        console.log(selectedOption);
        console.log("---------", data.data[selectedOption]);
        setMilestoneArr(data.data[selectedOption]);
        if (data.status == false) {
          Notification({ message: data.message, type: "error" });
          return;
        }
      })
      .catch((_error) => {
        Notification({ message: "Problem While Getting Issues", type: "error" });
      });
  }, [selectedProjectId, selectedOption]);

  const handlePageChange = (pageNumber: number) => {
    setCurrentPage(pageNumber);
  };

  const handleItemsPerPageChange = (newItemsPerPage: number) => {
    setCurrentPage(1)
    setItemsPerPage(newItemsPerPage);
  };
  const totalPages = Math.ceil(milestoneArr.length / itemsPerPage);
  const displayedMilestones = milestoneArr.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  return (
    <div className="relative">
      <table className="table-fixed w-full text-sm text-left rtl:text-right text-gray-500 dark:text-gray-400">
        <thead className="text-xs text-gray-700 uppercase bg-gray-100 dark:bg-gray-700 dark:text-gray-400">
          <tr>
            <th scope="col" className="px-6 py-3 rounded-s-lg">
              Milestones
            </th>
            <th scope="col" className="px-6 py-3 text-center">
              Graph
            </th>

          </tr>
        </thead>
        <tbody>
          {displayedMilestones.map((milestone) => (
            <tr className="bg-white dark:bg-gray-800 border-b" key={milestone.title}>
              <th scope="row" className="px-6 py-4 whitespace-nowrap dark:text-white cursor-default">
                <p className="font-medium text-gray-900">
                  <b>{milestone.title}</b> - Group Milestone
                </p>
                <div>
                  {milestone.start_date} - {milestone.due_date}
                </div>
              </th>
              <td className="px-6 py-4">
                <div className="w-full bg-gray-200 rounded-full h-1.5 mb-4 dark:bg-gray-700" style={{ width: 400 }}>
                  {milestone.issues && (
                    <div className="flex justify-between">
                      <div className="bg-green-600 h-1.5 rounded-full dark:bg-blue-500" style={{ width: `${percentage(milestone.issues)}%` }}></div>
                      <div>.</div>
                      <div className="text-left">
                        {milestone.issues.reduce((acc, issue) => acc + issue.count, 0)} issues
                        <span className="text-right">{percentage(milestone.issues)}% complete</span>
                      </div>
                    </div>
                  )}
                </div>
              </td>

            </tr>
          ))}
        </tbody>
      </table>
      <div className="flex justify-center mt-4">
        <div className="flex items-center mr-4">
          <label className="mr-2">Items per page:</label>
          <select value={itemsPerPage} onChange={(e) => handleItemsPerPageChange(parseInt(e.target.value, 10))}>
            <option value={10}>10</option>
            <option value={20}>20</option>
            <option value={50}>50</option>
          </select>
        </div>
        <button
          className="px-4 py-2 mx-1 text-sm font-medium rounded-md"
          onClick={() => handlePageChange(currentPage - 1)}
          disabled={currentPage === 1}
        >
          Prev
        </button>
        <button
          className="px-4 py-2 mx-1 text-sm font-medium rounded-md"
          onClick={() => handlePageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
        >
          Next
        </button>
      </div>
    </div>
   
  );
};

export default MileStoneTable;
