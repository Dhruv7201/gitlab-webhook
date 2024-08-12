import React, { useState } from "react";
import EditableDropdown from "../components/_ui/EditableDropdown";
import { DatePickerWithRange } from "@/utils/DateRange";
import MileStoneTable from "@/components/_ui/MilestoneTable";
import { DateRange } from "react-day-picker";

const monthAgo = () => {
  const date = new Date();
  date.setMonth(date.getMonth() - 1);
  return date;
};

const Milestones = () => {
  const [selectedProjectId, setSelectedProjectId] = React.useState(0);
  const [selectedOption, setSelectedOption] = useState("ongoing_milestones");
  const [date, setDate] = React.useState<DateRange>({
    from: monthAgo(),
    to: new Date(),
  });

  const time = "2 Hours";

  return (
    <div className="flex flex-col">
      <div className="p-4 flex flex-col md:flex-row gap-4">
        <EditableDropdown setSelectedProjectId={setSelectedProjectId} />
        <DatePickerWithRange date={date} setDate={setDate} />
      </div>

      <div className="p-4">
        <div className="p-4">
          <ul className="flex gap-4 font-medium">
            <li onClick={() => setSelectedOption("ongoing_milestones")}>
              <div
                className={`px-4 py-2 rounded-full cursor-pointer ${
                  selectedOption === "ongoing_milestones"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-200 text-gray-700 hover:bg-gray-300 hover:text-gray-800"
                }`}
              >
                <span className="font-semibold">On-Going</span>
                <span className="ml-2">{time}</span>
              </div>
            </li>
            <li onClick={() => setSelectedOption("completed_milestones")}>
              <div
                className={`px-4 py-2 rounded-full cursor-pointer ${
                  selectedOption === "completed_milestones"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-200 text-gray-700 hover:bg-gray-300 hover:text-gray-800"
                }`}
              >
                <span className="font-semibold">Closed</span>
              </div>
            </li>
            <li onClick={() => setSelectedOption("all_milestones")}>
              <div
                className={`px-4 py-2 rounded-full cursor-pointer ${
                  selectedOption === "all_milestones"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-200 text-gray-700 hover:bg-gray-300 hover:text-gray-800"
                }`}
              >
                <span className="font-semibold">All</span>
              </div>
            </li>
          </ul>
        </div>
      </div>

      <div className="p-4 flex-1">
        <MileStoneTable
          selectedProjectId={selectedProjectId}
          selectedOption={selectedOption}
        />
      </div>
    </div>
  );
};

export default Milestones;
