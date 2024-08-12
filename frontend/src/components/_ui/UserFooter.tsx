import api from "@/utils/api";
import * as React from "react";
import "./issueFooter.css";
import { ListFilter } from "lucide-react";
import Notification from "@/Notification";
import { secondsToHMSorDays } from "@/utils/timeFormate";

interface Props {
  selectedUserId: number;
}

type ChartData = {
  start_time: string;
  duration: number;
  issue_name: string;
  issue_url: string;
  percentage: number;
};

const UserFooter: React.FC<Props> = ({ selectedUserId }) => {
  const [userWorkArr, setUserWorkArr] = React.useState<ChartData[]>([]);
  const [sortOrder, setSortOrder] = React.useState<"asc" | "desc">("asc");

  React.useEffect(() => {
    api
      .post("/get_work_duration_time", {
        userId: Number(selectedUserId),
      })
      .then((response) => {
        if (!response.data.status) {
          Notification({ message: response.data.message, type: "error" });
        }
        const sortedData = response.data.data.sort(
          (a: ChartData, b: ChartData) => {
            return sortOrder === "asc"
              ? new Date(a.start_time).getTime() -
                  new Date(b.start_time).getTime()
              : new Date(b.start_time).getTime() -
                  new Date(a.start_time).getTime();
          }
        );
        setUserWorkArr(sortedData);
      });
  }, [selectedUserId, sortOrder]);

  const toggleSortOrder = () => {
    setSortOrder((prevOrder) => (prevOrder === "asc" ? "desc" : "asc"));
  };

  return (
    <div className="flex flex-col items-center justify-center space-y-4 w-full mt-4 p-4 rounded-md shadow-md overflow-y-auto">
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
      <div key={0} className="w-full bg-white p-4 rounded-md shadow-md">
        <div className="flex justify-between items-center">
          <div
            className="w-3/4 text-center bg-green-100 p-2 rounded-md cursor-pointer"
            title="Issue Name"
          >
            Issue Name
          </div>
          <div className="w-1/4 text-center bg-blue-100 p-2 rounded-md">
            Time Spent
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
            <div
              className="w-3/4 text-start bg-green-100 p-2 rounded-md cursor-pointer underline"
              title={work.issue_name}
            >
              <a href={work.issue_url} target="_blank" rel="noreferrer">
                {work.issue_name.length > 80
                  ? work.issue_name.slice(0, 80) + "..."
                  : work.issue_name}
              </a>
            </div>
            <div className="w-1/4 text-center bg-blue-100 p-2 rounded-md">
              {secondsToHMSorDays(work.duration)}
            </div>

            <div className="w-1/4 text-center bg-yellow-100 p-2 rounded-md">
              {work.percentage.toFixed(2)}%
            </div>
            <div className="w-1/4 text-center bg-red-100 p-2 rounded-md">
              {work.start_time.replace("T", " ").replace("Z", "").slice(0, -4)}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default UserFooter;
