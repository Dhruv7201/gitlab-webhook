import React from "react";
import api from "@/utils/api";
import { useState, useEffect } from "react";
import Notification from "../../Notification";
import { Button } from "./button";
import { Progress } from "./progress";

type issuesObject = {
  _id: string;
  count: number;
};

const percentage = (issues: issuesObject[]): number => {
  const closed = issues
    .filter((issue) => issue._id === "closed")
    .reduce((acc, issue) => acc + issue.count, 0);
  const all_issues = issues.reduce(
    (acc: number, issue) => acc + issue.count,
    0
  );
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

const MileStoneTable: React.FC<Props> = ({
  selectedProjectId,
  selectedOption,
}) => {
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
        setMilestoneArr(data.data[selectedOption]);
        if (data.status == false) {
          Notification({ message: data.message, type: "error" });
          return;
        }
      })
      .catch((_error) => {
        Notification({
          message: "Problem While Getting Issues",
          type: "error",
        });
      });
  }, [selectedProjectId, selectedOption]);

  const handlePageChange = (pageNumber: number) => {
    setCurrentPage(pageNumber);
  };

  const handleItemsPerPageChange = (newItemsPerPage: number) => {
    setCurrentPage(1);
    setItemsPerPage(newItemsPerPage);
  };
  const totalPages = Math.ceil(milestoneArr.length / itemsPerPage);
  const displayedMilestones = milestoneArr.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  return (
    <div className="relative">
      <table className="table-auto w-full text-sm text-left rtl:text-right text-gray-500 dark:text-gray-400">
        <thead className="text-xs text-gray-700 uppercase bg-gray-100 dark:bg-gray-700 dark:text-gray-400">
          <tr>
            <th scope="col" className="px-4 py-2 md:px-6 md:py-3 rounded-s-lg">
              Milestones
            </th>
            <th scope="col" className="px-4 py-2 md:px-6 md:py-3 text-center">
              Graph
            </th>
          </tr>
        </thead>
        <tbody>
          {displayedMilestones.map((milestone) => (
            <tr
              className="bg-white dark:bg-gray-800 border-b"
              key={milestone.title}
            >
              <th
                scope="row"
                className="px-4 py-2 md:px-6 md:py-4 whitespace-nowrap dark:text-white cursor-default"
              >
                <p className="font-medium text-gray-900 text-sm md:text-base">
                  <b>{milestone.title}</b> - Group Milestone
                </p>
                <div className="text-xs md:text-sm">
                  {milestone.start_date} - {milestone.due_date}
                </div>
              </th>
              <td className="px-4 py-2 md:px-6 md:py-4">
                <div className="relative w-full bg-gray-200 rounded-full h-1.5 mb-4 dark:bg-gray-700">
                  {milestone.issues && (
                    <div>
                      <Progress value={percentage(milestone.issues)} />
                      <div className="flex flex-col md:flex-row justify-between items-center md:items-baseline">
                        <span className="text-xs md:text-sm">
                          {milestone.issues.reduce(
                            (acc, issue) => acc + issue.count,
                            0
                          )}
                          issues
                        </span>
                        <span className="text-xs md:text-sm mt-1 md:mt-0">
                          {percentage(milestone.issues)}% complete
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="flex flex-col md:flex-row justify-between items-center mt-4 px-4 md:px-0">
        <div
          className={`flex items-center mb-4 md:mb-0 ${
            milestoneArr.length <= 10 ? "hidden" : "visible"
          }`}
        >
          <label className="mr-2">Items per page:</label>
          <select
            value={itemsPerPage}
            onChange={(e) =>
              handleItemsPerPageChange(parseInt(e.target.value, 10))
            }
            className="bg-white border border-gray-300 rounded-md text-gray-700 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-300"
          >
            <option value={10}>10</option>
            <option
              className={`${milestoneArr.length <= 20 ? "hidden" : "visible"}`}
              value={20}
            >
              20
            </option>
            <option
              className={`${milestoneArr.length <= 50 ? "hidden" : "visible"}`}
              value={50}
            >
              50
            </option>
          </select>
        </div>
        <div className="inline-flex space-x-2">
          <Button
            onClick={() => handlePageChange(currentPage - 1)}
            style={{ color: `${currentPage === 1 ? "grey" : "white"}` }}
            className="mr-2"
            disabled={currentPage === 1}
          >
            Prev
          </Button>
          <Button
            style={{
              color: `${currentPage === totalPages ? "grey" : "white"}`,
            }}
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  );
};

export default MileStoneTable;
