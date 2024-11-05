import React, { useEffect } from "react";
import {
  createColumnHelper,
  useReactTable,
  getCoreRowModel,
  flexRender,
} from "@tanstack/react-table";
import { useForm, Controller } from "react-hook-form";
import EditableDropdown from "@/components/_ui/EditableDropdown";
import { DatePicker } from "@/utils/DatePicker";
import api from "@/utils/api";
import { format } from "date-fns";

const DailyReport = () => {
  const { control, handleSubmit, setValue, reset } = useForm();
  const [selectedProjectId, setSelectedProjectId] = React.useState(0);
  const [selectedDate, setSelectedDate] = React.useState<Date | undefined>(
    undefined
  );
  const [data, setData] = React.useState<any[]>([]);

  // Initialize selected date to current date
  useEffect(() => {
    if (selectedDate === undefined) {
      setSelectedDate(new Date());
    }
  }, []);

  const getLevel = () => {
    const jwt = localStorage.getItem("token");
    if (!jwt) return false;
    const jwtData = jwt.split(".")[1];
    const decodedJwtJsonData = window.atob(jwtData);
    const decodedJwtData = JSON.parse(decodedJwtJsonData);
    return decodedJwtData.level;
  };

  const level = getLevel();

  // Fetch the data when selectedProjectId or selectedDate changes
  useEffect(() => {
    const fetchData = async () => {
      if (!selectedDate) return;

      try {
        const date = format(selectedDate, "yyyy-MM-dd");

        const response = await api.post("/daily_report", {
          project_id: selectedProjectId,
          selected_date: date,
        });

        // Ensure issue_url is included in the mapped result
        const result = response.data.map((item: any) => ({
          id: item.id,
          name: item.name,
          issue_url: item.issue_url, // Include issue_url from the response
          assignedTo: item.assigned_to,
          milestone: item.milestone,
          status: item.status,
          dueDate: item.due_date,
          efforts: item.efforts,
          comments: item.comments,
        }));

        setData(result);
        reset({ data: result }); // Reset form with fetched data
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, [selectedProjectId, selectedDate]);

  const handleInputChange = (
    index: number,
    field: string,
    value: string | number
  ) => {
    setValue(`data[${index}].${field}`, value);
  };

  const columnHelper = createColumnHelper<any>();

  const columns = [
    columnHelper.accessor("id", { header: "ID" }),
    columnHelper.accessor("name", {
      header: "Name",
      cell: (info) => {
        const maxWords = 6;
        const fullTitle = info.getValue();
        const truncatedTitle =
          fullTitle.split(" ").slice(0, maxWords).join(" ") +
          (fullTitle.split(" ").length > maxWords ? "..." : "");
        const issueUrl = info.row.original.issue_url;

        // Ensure issueUrl is not undefined
        if (!issueUrl) {
          return <span>{truncatedTitle}</span>;
        }

        return (
          <a
            href={issueUrl}
            target="_blank"
            rel="noopener noreferrer"
            title={fullTitle} // Full title on hover
            className="text-blue-600 hover:underline"
          >
            {truncatedTitle}
          </a>
        );
      },
    }),
    columnHelper.accessor("assignedTo", { header: "Assigned To" }),
    columnHelper.accessor("milestone", { header: "Milestone" }),
    columnHelper.accessor("status", { header: "Status" }),
    columnHelper.accessor("dueDate", { header: "Due Date" }),
    columnHelper.accessor("efforts", {
      header: "Efforts (hrs)",
      cell: (info) => (
        <Controller
          control={control}
          name={`data[${info.row.index}].efforts`}
          render={({ field }) => (
            <input
              type="number"
              {...field}
              className="border border-gray-300 p-1"
              onChange={(e) =>
                handleInputChange(info.row.index, "efforts", e.target.value)
              }
            />
          )}
        />
      ),
    }),
    columnHelper.accessor("comments", {
      header: "Comments",
      cell: (info) => (
        <Controller
          control={control}
          name={`data[${info.row.index}].comments`}
          render={({ field }) => (
            <input
              type="text"
              {...field}
              className="border border-gray-300 p-1"
              onChange={(e) =>
                handleInputChange(info.row.index, "comments", e.target.value)
              }
              disabled={level === "user"} // Disable input for non-admin users
            />
          )}
        />
      ),
    }),
  ];

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  const onSubmit = async (formData: any) => {
    try {
      const response = await api.post("/daily_report_comments", {
        project_id: selectedProjectId,
        date: selectedDate?.toISOString().split("T")[0],
        username: localStorage.getItem("username"),
        data: formData.data,
      });

      const result = response.data;
      if (result.status === false) {
        console.error("Error submitting data:", result.message);
        return;
      }
    } catch (error) {
      console.error("Error submitting data:", error);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="p-4">
      <div className="flex justify-between items-center">
        <div className="flex gap-4">
          <EditableDropdown
            setSelectedProjectId={setSelectedProjectId}
            selectedProjectId={selectedProjectId}
          />
          <DatePicker date={selectedDate} setDate={setSelectedDate} />
        </div>

        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded-lg"
        >
          Submit Report
        </button>
      </div>
      <table className="min-w-full bg-white border border-gray-200 mt-4">
        <thead className="bg-gray-100 text-gray-600 uppercase text-sm leading-normal">
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <th key={header.id} className="py-3 px-6 text-left">
                  {flexRender(
                    header.column.columnDef.header,
                    header.getContext()
                  )}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody className="text-gray-600 text-sm">
          {table.getRowModel().rows.map((row) => (
            <tr
              key={row.id}
              className="border-b border-gray-200 hover:bg-gray-100"
            >
              {row.getVisibleCells().map((cell) => (
                <td key={cell.id} className="py-3 px-6 text-left">
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </form>
  );
};

export default DailyReport;

