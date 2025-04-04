def Plot_Sensitivity(df, outDict : dict):
    import itertools
    paramList = ['Room Width [m]',
                'Wing Length [m]',
                'Number of Wings [/]',
                'Room Length [m]',
                'WWR [%]',
                'Orientation [/]',
                'Spatial Distribution [/]',
                'Insulation Material [/]']
    sensiList = []

    for metric in outDict.keys():
        outList = outDict[metric]

        #pre-filtering the df to calculate the average result
        for param in outList:
            paramValue = list(df[param].unique())[0]
            tempDF = df[df[param] == paramValue]
        average = tempDF[metric].mean()

        sensiDict = {}
        
        paramOutDict = {}
        for paramOut in outList:
            paramOutDict[paramOut] = list(df[paramOut].unique())[0]

        inList = [param for param in paramList if param not in outList]

        for param in inList:
            sensiDict[param] = []
            # initialise the dict with the fixed params.
            tempParamDict = {}
            for paramOut in outList:
                tempParamDict[paramOut] = [paramOutDict[paramOut]]

            for paramIn in [paramTemp for paramTemp in inList if paramTemp != param]:
                unique_values = list(df[paramIn].unique())
                tempParamDict[paramIn] = unique_values

            combinations = list(itertools.product(*tempParamDict.values()))

            # Convert combinations into a list of dictionaries
            combinations_dict = [dict(zip(tempParamDict.keys(), combo)) for combo in combinations]
            
            for combo in combinations_dict:
                
                filtered_df = df
                for parameter, value in combo.items():
                    filtered_df = filtered_df[filtered_df[parameter] == value]
                values = list(filtered_df[metric])
                valuesNumber = len(values)

                if valuesNumber > 1:
                    for i in range(1, valuesNumber):
                        sensiDict[param].append(abs(values[i] - values[i-1]) / average *100)
                    
                    if param in ['Orientation [/]', 'Spatial Distribution [/]', 'Insulation Material [/]'] and valuesNumber > 2:
                        sensiDict[param].append(abs(values[0] - values[-1]) / average *100)

        sensiList.append(sensiDict)
        print(metric, 'done')


    import matplotlib.pyplot as plt

    titles = ['SDA 50%', 'Thermal\nEnergy\nDemand', 'Embodied\nEnergy']
    groupColors = ['#A7C7E7',  # Pastel Blue
                    '#87CEEB',  # Sky Blue
                    '#76D7C4',  # Light Teal
                    '#66CDAA',  # Medium Aquamarine
                    '#57C785',  # Soft Mint Green
                    '#7EC850',  # Light Green
                    '#9CD54A',  # Yellow-Green
                    '#B5E655']  # Pastel Lime Green

    # Create figure with 3 subplots side by side
    fig, axes = plt.subplots(1, 3)  # Removed sharey=True

    for idx, (sensiDict, ax, title) in enumerate(zip(sensiList, axes, titles)):

        box_data = []
        y_labels = []
        colors = []
        
        counter = 0
        for param in sensiDict.keys():
            values = sensiDict[param]
            box_data.append(values)
            y_labels.append(f'{param[:-4]}')
            colors.append(groupColors[counter])

            if idx == 2 and param in ["WWR [%]", 'Wing Length [m]']:
                box_data.append([])
                y_labels.append('')
                colors.append('white')
                counter += 1

            counter += 1

        if idx == 1:
            box_data.append([])
            y_labels.append(f'Spatial Distribution')
            colors.append('white')

            box_data.append([])
            y_labels.append(f'Insulation Material')
            colors.append('white')

        elif idx == 0:
            box_data.append([])
            y_labels.append(f'Insulation Material')
            colors.append('white')

        # Plot boxplots
        box = ax.boxplot(box_data, vert = False, patch_artist=True, widths=0.6, flierprops=dict(marker='.', markersize=3, color='black'), medianprops=dict(color="white", linewidth=1))

        # Set colors for each box
        for patch, color in zip(box['boxes'], colors):
            patch.set_facecolor(color)
        
        # Show the 0-axis
        ax.axvline(0, color='black', linestyle='--', linewidth=1)

        # Set title
        ax.set_title(title)
        ax.set_xlabel('Relative\nVariation\nInduced [%]')
        ax.set_yticklabels(y_labels if idx == 0 else [])  # **Only first plot gets y-labels**

        if idx != 0:
            ax.tick_params(left=False)  # Hide ticks for other subplots

    # Adjust layout
    plt.tight_layout()
    plt.show()



outDict = {'Spatial Daylight Autonomy 50% [%]' : ['Insulation Material [/]'],
           'Total Energy Need [kWh/m²]' : ['Spatial Distribution [/]','Insulation Material [/]'],
           'Total Embodied Energy/Area [MJ/m²]' : ['Number of Wings [/]','Orientation [/]']}