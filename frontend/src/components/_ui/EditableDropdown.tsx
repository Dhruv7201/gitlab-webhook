"use client";
import api from "@/utils/api";
import Notification from "../../Notification";
import * as React from "react";
import { ChevronsUpDown } from "lucide-react";
import { Button } from "@/components/_ui/button";
import { Command } from "@/components/_ui/command";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/_ui/popover";

type Project = {
  id: number;
  name: string;
};
interface Props {
  setSelectedProjectId: (id: number) => void;
}

const EditableDropdown: React.FC<Props> = ({ setSelectedProjectId }) => {
  const [open, setOpen] = React.useState(false);
  const [value, setValue] = React.useState("");
  const [availableProject, setAvailableProject] = React.useState(false);
  const [selectedProjectName, setSelectedProjectName] =
    React.useState("Select Project");

  const [projects, setProjects] = React.useState<Project[]>([]);

  React.useEffect(() => {
    api
      .post("/projects")
      .then((response) => {
        const data = response.data;
        if (data.status == false) {
          Notification({ message: data.message, type: "error" });
          return;
        }
        setProjects(data.data);
      })
      .catch((_error) => {
        Notification({ message: "Problem fetching users", type: "error" });
      });
  }, []);

  function onSearchButtonClick(project: { id: number; name: string }) {
    setSelectedProjectId(Number(project.id));
    setValue("");
    setSelectedProjectName(project.name);
    setOpen(false);
  }

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          className="w-[200px] justify-between"
          aria-expanded="true"
          data-state="opened"
        >
          <span>{selectedProjectName}</span>
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="p-4">
        <Command>
          <div>
            <input
              type="text"
              autoFocus
              onChange={(e) => {
                setAvailableProject(false);
                setValue(e.target.value);
              }}
              value={value}
              className="w-full p-2 border border-gray-300 mb-4"
              placeholder="Search Projects..."
            />
            <div>
              {projects
                .filter((item) => {
                  if (value == "") {
                    return true;
                  }
                  const input_value = value.toLowerCase();
                  const item_value = item.name.toLowerCase();
                  return input_value && item_value.startsWith(input_value);
                })
                .map((project) => (
                  <h1
                    key={project.id}
                    onClick={() => {
                      onSearchButtonClick(project);
                    }}
                    className="cursor-pointer p-2 hover:bg-gray-100 rounded"
                  >
                    {project.name}
                  </h1>
                  // add default value as view all projects
                  

                ))}
                {projects.length > 0 && (
                <h1
                  onClick={() => {
                    setSelectedProjectId(0);
                    setValue("");
                    setSelectedProjectName("View All Projects");
                    setOpen(false);
                  }}
                  className="cursor-pointer p-2 hover:bg-gray-100 rounded"
                >
                  View All Projects
                </h1>
              )}
              {availableProject && <h1 className="p-2">No project found</h1>}
            </div>
          </div>
        </Command>
      </PopoverContent>
    </Popover>
  );
};

export default EditableDropdown;
