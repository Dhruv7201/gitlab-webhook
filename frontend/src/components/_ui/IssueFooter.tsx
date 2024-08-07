import api from "@/utils/api";
import * as React from "react";
import "./issueFooter.css";
import { ListFilter } from "lucide-react";

interface Props {
  selectedIssueId: number;
}

type Label_info = {
  start_time: string;
  label: string;
  duration: number;
  percentage: number;
};

type ChartData = {
  name: string;
  label_info: Label_info;
};

const IssueFooter: React.FC<Props> = ({ selectedIssueId }) => {
  const [userWorkArr, setUserWorkArr] = React.useState<ChartData[]>([]);
  const [sortOrder, setSortOrder] = React.useState<"asc" | "desc">("asc");

  React.useEffect(() => {
    api
      .post("/get_user_by_work", {
        issue_id: Number(selectedIssueId),
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

  const msToTime = (duration: number) => {
    const seconds = Math.floor((duration / 1000) % 60);
    const minutes = Math.floor((duration / (1000 * 60)) % 60);
    const hours = Math.floor((duration / (1000 * 60 * 60)) % 24);

    return `${hours}h ${minutes}m ${seconds}s`;
  };

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
      {userWorkArr.map((work, index) => (
        <div key={index} className="w-full bg-white p-4 rounded-md shadow-md">
          <div className="flex justify-between items-center">
            <div className="w-1/4 text-center bg-blue-100 p-2 rounded-md">
              {msToTime(work.label_info.duration)}
            </div>
            <div className="w-1/4 text-center bg-green-100 p-2 rounded-md">
              {work.name}
            </div>
            <div className="w-1/4 text-center bg-yellow-100 p-2 rounded-md">
              {work.label_info.percentage.toFixed(2)}%
            </div>
            <div className="w-1/4 text-center bg-red-100 p-2 rounded-md">
              {work.label_info.start_time
                .replace("T", " ")
                .replace("Z", "")
                .slice(0, -4)}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default IssueFooter;
