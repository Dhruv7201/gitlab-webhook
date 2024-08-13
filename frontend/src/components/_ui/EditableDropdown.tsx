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
  selectedProjectId: number;
}

const EditableDropdown: React.FC<Props> = ({
  setSelectedProjectId,
  selectedProjectId,
}) => {
  const [open, setOpen] = React.useState(false);
  const [value, setValue] = React.useState("");
  const [selectedProjectName, setSelectedProjectName] =
    React.useState<string>("Select Project");

  const [projects, setProjects] = React.useState<Project[]>([]);
  const [isDataLoaded, setIsDataLoaded] = React.useState(false);

  // Fetch projects and initialize selected project ID
  React.useEffect(() => {
    api
      .post("/projects")
      .then((response) => {
        const data = response.data;
        if (data.status === false) {
          Notification({ message: data.message, type: "error" });
          return;
        }
        setProjects(data.data);
        setIsDataLoaded(true);

        // Initialize selected project ID from local storage
        const storedProjectId = localStorage.getItem("selectedProjectId");
        if (storedProjectId) {
          const id = Number(storedProjectId);
          if (data.data.some((project: Project) => project.id === id)) {
            setSelectedProjectId(id);
          }
        }
      })
      .catch((_error) => {
        Notification({ message: "Problem fetching projects", type: "error" });
      });
  }, [setSelectedProjectId]);

  React.useEffect(() => {
    // Update the selected project name based on selectedProjectId and projects
    if (isDataLoaded) {
      const project = projects.find(
        (project) => Number(project.id) === selectedProjectId
      );
      if (project) {
        setSelectedProjectName(project.name);
      }
    }
  }, [selectedProjectId, projects, isDataLoaded]);

  function onSearchButtonClick(project: Project) {
    setSelectedProjectId(Number(project.id));
    setValue("");
    setSelectedProjectName(project.name);
    setOpen(false);
    localStorage.setItem("selectedProjectId", project.id.toString());
  }

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          className="justify-between"
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
                setValue(e.target.value);
              }}
              value={value}
              className="w-full p-2 border border-gray-300 mb-4"
              placeholder="Search Projects..."
            />
            <div>
              {projects
                .filter((item) => {
                  if (value === "") {
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
                    className={`cursor-pointer p-2 hover:bg-gray-100 rounded ${
                      project.name === selectedProjectName ? "bg-gray-100" : ""
                    }`}
                  >
                    {project.name}
                  </h1>
                ))}
              {projects.length > 0 && (
                <h1
                  onClick={() => {
                    setSelectedProjectId(0);
                    setValue("");
                    setSelectedProjectName("View All Projects");
                    setOpen(false);
                    localStorage.setItem("selectedProjectId", "0");
                  }}
                  className="cursor-pointer p-2 hover:bg-gray-100 rounded"
                >
                  View All Projects
                </h1>
              )}
            </div>
          </div>
        </Command>
      </PopoverContent>
    </Popover>
  );
};

export default EditableDropdown;
