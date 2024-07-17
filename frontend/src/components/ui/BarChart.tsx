"use client"
import * as React from "react";

import { Bar, BarChart, CartesianGrid, LabelList, XAxis } from "recharts"
import Notification from "../../Notification";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart"
// const barData = [{'name': 'vedanthakur0404005', 'time_waste': 11.42}, {'name': 'rahulpandey0404005', 'time_waste': 11.42}]

const chartConfig = {
  desktop: {
    label: "Desktop",
    color: "hsl(var(--chart-1))",
    format:"time_formats"
  },
} as ChartConfig

type BarData = {
  name: string;
  time_waste: string;
  format: any
};

type Project = {
  id: string;
  name: string;
};

export function Barchart() {
  const api = import.meta.env.VITE_API_URL;

  const [barData, setBarData] = React.useState<BarData[]>([]);
  const [projects, setProjects] = React.useState<Project[]>([]);


  React.useEffect(() => {
    const get_projects = async ()=>{
    try {
      const response = await fetch(api + "/projects");
      const data = await response.json();
      setProjects(data.data);
    } catch (error) {
      Notification({ message: "Problem fetching users", type: "error" });
    }
  }
  get_projects()
  }, []);


  const fetchData = async (project_id: any) => {
    
    try {
      // const project_id = 59516973
      const response = await fetch(api + `/user_time_waste/${project_id}`);
      const data = await response.json();


      setBarData(data);
    } catch (error) {
      console.error("Problem fetching data", error);
    }
  }

  const renderLabel = (props: any) => {
  
    const  seconds = props
    var min = null
    var hr = null
    var sec = null

    hr = Math.floor(seconds / 3600)
    if (hr == 0){hr = '00'}

    min = Math.floor(((seconds % 3600) / 60))
    if (min == 0){min = '00'}

    sec = Math.floor(seconds % 60)

    

    return `${hr}:${min}:${sec}`;
};


const renderLabel1 = (props: any) => {
  
  const  seconds = props
  var min = null
  var hr = null
  var sec = null

  hr = Math.floor(seconds / 3600)
  if (hr == 0){hr = '00'}

  min = Math.floor(((seconds % 3600) / 60))
  if (min == 0){min = '00'}

  sec = Math.floor(seconds % 60)

  

  return <p><li className="marker:text-green-600">Time {hr}:{min}:{sec}</li></p>;
};
 
  return (
    <Card>
      <select
        defaultValue=""
        onChange={(e) => fetchData(e.target.value)}
        className="block py-2 px-4 rounded-md shadow-sm border-gray-300 focus:border-indigo-500 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 w-48"
      >
        <option value="" disabled>
          Choose user
        </option>
        {projects.map((project) => (
          <option key={project.id} value={project.id} className="text-gray-900">
            {project.name}
          </option>
        ))}
      </select>
      <CardHeader>
        <CardTitle>Bar Chart - Label</CardTitle>
        <CardDescription>January - June 2024</CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig}>
          <BarChart
            accessibilityLayer
            data={barData}
            margin={{
              top: 20,
            }}
          >
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="name"
              tickLine={false}
              tickMargin={10}
              axisLine={false}
              tickFormatter={(value) => value.slice(0, 3)}
            />
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent hideLabel />}
              formatter={renderLabel1}
            />
            <Bar dataKey="time_waste" fill="var(--color-desktop)" radius={8}>
              <LabelList
                position="top"
                offset={12}
                className="fill-foreground"
                fontSize={12}
                formatter={renderLabel}
              />
            </Bar>
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}