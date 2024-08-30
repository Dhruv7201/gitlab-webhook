import api from "@/utils/api";
import * as React from "react";
import "./issueFooter.css";
import { ListFilter } from "lucide-react";
import { secondsToHMSorDays } from "@/utils/timeFormate";

interface Props {
  selectedIssueId: number;
}

type LabelInfo = {
  start_time: string;
  label: string;
  duration: number;
  percentage: number;
};

type ChartData = {
  name: string;
  label_info: LabelInfo;
};

const IssueFooter: React.FC<Props> = ({ selectedIssueId }) => {
  const [userWorkArr, setUserWorkArr] = React.useState<ChartData[]>([]);
  const [sortOrder, setSortOrder] = React.useState<"asc" | "desc">("asc");

  React.useEffect(() => {
    api
      .post("/get_user_by_work", {
        issue_id: selectedIssueId,
      })
      .then((response) => {
        const sortedData = response.data.data.sort(
          (a: ChartData, b: ChartData) => {
            return sortOrder === "asc"
              ? new Date(a.label_info.start_time).getTime() -
                  new Date(b.label_info.start_time).getTime()
              : new Date(b.label_info.start_time).getTime() -
                  new Date(a.label_info.start_time).getTime();
          }
        );
        setUserWorkArr(sortedData);
      });
  }, [selectedIssueId, sortOrder]);

  const toggleSortOrder = () => {
    setSortOrder((prevOrder) => (prevOrder === "asc" ? "desc" : "asc"));
  };

  return (
    <div className="flex flex-col items-center justify-center space-y-4 w-full mt-4 bg-gray-100 p-4 rounded-md shadow-md">
      <div className="w-full flex justify-end">
        <button
          onClick={toggleSortOrder}
          className="mb-4 p-2 bg-blue-500 text-white rounded-md shadow-md"
        >
          Sort by Start Time
          {sortOrder === "asc" ? (
            <ListFilter size={16} className="inline-block ml-1" />
          ) : (
            <ListFilter
              size={16}
              className="inline-block ml-1 transform rotate-180"
            />
          )}
        </button>
      </div>
      <div className="w-full bg-white p-4 rounded-md shadow-md">
        <div className="flex justify-between items-center">
          <div className="w-1/4 text-center bg-green-100 p-2 rounded-md">
            User
          </div>
          <div className="w-1/4 text-center bg-purple-100 p-2 rounded-md">
            Label
          </div>
          <div className="w-1/4 text-center bg-blue-100 p-2 rounded-md">
            Duration
          </div>
          <div className="w-1/4 text-center bg-yellow-100 p-2 rounded-md">
            Percentage
          </div>
          <div className="w-1/4 text-center bg-red-100 p-2 rounded-md">
            Start Time
          </div>
        </div>
      </div>
      {userWorkArr.map((work, index) => (
        <div key={index} className="w-full bg-white p-4 rounded-md shadow-md">
          <div className="flex justify-between items-center">
            <div className="w-1/4 text-center bg-green-100 p-2 rounded-md">
              {work.name}
            </div>
            <div className="w-1/4 text-center bg-purple-100 p-2 rounded-md">
              {work.label_info.label}
            </div>
            <div className="w-1/4 text-center bg-blue-100 p-2 rounded-md">
              {secondsToHMSorDays(work.label_info.duration)}
            </div>

            <div className="w-1/4 text-center bg-yellow-100 p-2 rounded-md">
              {work.label_info.percentage.toFixed(2)}%
            </div>
            <div className="w-1/4 text-center bg-red-100 p-2 rounded-md">
              {new Date(work.label_info.start_time).toLocaleString()}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default IssueFooter;
