import React from "react";
import { useEffect } from "react";
import EditableDropdown from "@/components/_ui/EditableDropdown";
import { DatePicker } from "@/utils/DatePicker";
import api from "@/utils/api";
import { format } from "date-fns";
import { useReactTable } from "@tanstack/react-table";
import { getCoreRowModel } from "@tanstack/react-table";
import { createColumnHelper } from "@tanstack/react-table";
import { flexRender } from "@tanstack/react-table";

const ReleasePlan = () => {
  const [data, setData] = React.useState<any[]>([]);
  const [selectedProjectId, setSelectedProjectId] = React.useState(0);
  const [selectedDate, setSelectedDate] = React.useState<Date | undefined>(
    undefined
  );

  useEffect(() => {
    if (selectedDate === undefined) {
      setSelectedDate(new Date());
    }
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      if (!selectedDate) return;

      try {
        const date = format(selectedDate, "yyyy-MM-dd");

        const response = await api.post("/release_plan", {
          project_id: selectedProjectId,
          selected_date: date,
        });

        const result = response.data.map((item: any) => ({
          id: item.id,
          iid: item.iid,
          title: item.title, // Include title
          issue_url: item.url, // Use the correct field for issue URL
          due_date: item.due_date, // Include due_date
          created_at: item.created_at, // Include created_at
          project_name: item.project_name, // Include project_name
          status: item.status, // Include status
        }));

        setData(result);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, [selectedProjectId, selectedDate]);
  const columnHelper = createColumnHelper<any>();

  const columns = [
    columnHelper.accessor("iid", { header: "IID" }),
    columnHelper.accessor("title", { header: "Title" }),
    columnHelper.accessor("issue_url", {
      header: "Issue URL",
      cell: (cell: any) => (
        <a
          href={cell.getValue()}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-500 underline"
        >
          {cell.getValue()}
        </a>
      ),
    }),
    columnHelper.accessor("due_date", { header: "Due Date" }),
    columnHelper.accessor("created_at", { header: "Created At" }),
    columnHelper.accessor("project_name", { header: "Project Name" }),
    columnHelper.accessor("status", { header: "Status" }),
  ];

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });
  return (
    <div className="p-4">
      <div className="flex justify-between items-center">
        <div className="flex gap-4">
          <EditableDropdown
            setSelectedProjectId={setSelectedProjectId}
            selectedProjectId={selectedProjectId}
          />
          <DatePicker date={selectedDate} setDate={setSelectedDate} />
        </div>
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
    </div>
  );
};

export default ReleasePlan;
