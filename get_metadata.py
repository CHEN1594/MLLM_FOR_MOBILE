# 在决定使用哪个模型
# input:svg file
# process: 
# 1. auto screenshot
# 2. use the following prompt to get the metadata

'''
can you see clearly of this photo? (attach the photo)
'''

'''
**【Task Description】**
You are a professional data visualization analyst. Output the details in JSON format following the template given, do not use python, do not forget origin text like 0: 


### **【JSON Template】**

Please strictly follow the JSON format below for output:

{
  "x":  
    {
      "type": "x",
      "main": true,  
      "attr_type": "Categorical",  
      "fixed_distance": "wait",  
      "range": { 
        "begin": "wait",
        "end": "wait"
      },
      "tick": [
        {
          "position": { "x": "wait", "y": "wait" },
          "content": "Apr"
        },
        {
          "position": { "x": "wait", "y": "wait" },
          "content": "May"
        }
      ]
    },
  "y":  
    {
      "type": "y",
      "main": false,  
      "attr_type": "Categorical",  
      "fixed_distance": "wait",  
      "range": { 
        "begin": "wait",
        "end": "wait"
      },
      "tick": [
        {
          "position": { "x": "wait", "y": "wait" },
          "content": "Low"
        },
        {
          "position": { "x": "wait", "y": "wait" },
          "content": "High"
        }
      ]
    }
}


------

### **【Rules Explanation】**

1. **"type"**: Specifies the type of the axis:
   - "x" represents the X-axis.
   - "y" represents the Y-axis.
2. **"main"**:
   - If the **chart is vertical** (e.g., **Bar Chart**), the X-axis is the base ("main": true), and the Y-axis is the numerical axis ("main": false).
   - If the **chart is horizontal** (e.g., **Horizontal Bar Chart**), the Y-axis is the base ("main": true), and the X-axis is the numerical axis ("main": false).
3. **"attr_type"**:
   - "Quantitative": The axis represents **quantitative (numerical) data**.(e.g., population, sales, height, temperature, or any other real-valued numerical measurement)
   - "Categorical": The axis represents **categorical (discrete) data**. Years (e.g., 2020, 2021, 2022, etc.) should always be treated as categorical variables, as they represent distinct labels rather than a continuous numerical scale.
4. **"fixed_distance"**: This field should always be "wait", indicating that the spacing between ticks will be calculated later.
5. **"range"**:
   - "begin": "wait"
   - "end": "wait"
   - These values represent the starting and ending coordinates of the axis and should always be "wait".
6. **"tick"**: Stores all tick marks on the axis:
   - **"position"**: The coordinate position of the tick mark (both "x" and "y" should always be "wait").
   - **"content"**: The textual label of the tick mark (e.g., "Jan", "Feb", etc.).
   
   '''