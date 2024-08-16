DOCS = """<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge">
	<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
	<title>API</title>
	<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/water.css@2/out/water.css">
	<script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
</head>
<body>
<div id="app">
	<div v-for="(api, index) in apis">
		<h2>{{ api.url }}</h2>
		<span>{{ api.docs }} </span>
		<form :method="api.method" :action="api.url" onsubmit="sendJSON(event)">
			<FormParam v-for="p in api.params" :p="p">
				<h4>
                    <span>{{ p.name }}</span><span v-if="p.required">*</span><span v-if="p.has_default"> - Default: {{ p.default }}</span>
                </h4>

				<!-- TODO default... -->
				<template v-if="p.type == 'str'">
					<input type="text" :name="p.name" :value="p.has_default ? p.default : ''"/>
				</template> 
				<template v-if="p.type == 'int'">
					<input type="number" :name="p.name" :value="p.has_default ? p.default : ''"/>
				</template> 
				<template v-if="p.type == 'bool'">
					<br/>
					<input type="checkbox" :name="p.name" :checked="(p.has_default && p.default)"/>
					<br/>
				</template> 
				<template v-if="p.type == 'enum'">	
					<span v-for="e in p.enums">
                        {{ e }}
						<template v-if="p.has_default && p.default == e">
							<input type="radio" :name="p.name" :value="e" checked/>
						</template>
						<template v-else>
							<input type="radio" :name="p.name" :value="e"/>
						</template>
					</span>
					{{ e }}<br/>
				</template>
				
			</FormParam>
			<input type="submit"></input>
		</form>

	</div>

</div>

<script>
  const { createApp } = Vue

        const FormParam = {
            template: `
				<span>{{ p.name }}</span><span v-if="p.required">*</span><span v-if="p.has_default"> - Default: {{ p.default }}</span>
				{{ p.type }}
				<!-- default... -->
				<template v-if="p.type == 'str'">
					<input type="text" :name="p.name" />
				</template> 
				<template v-if="p.type == 'int'">
					<input type="number" :name="p.name" />
				</template> 
				<template v-if="p.type == 'bool'">
					<br/>
					<input type="checkbox" :name="p.name" :checked="(p.has_default && p.default)"/>
					<br/>
				</template> 
				<template v-if="p.type == 'enum'">
					hey
				</template>
            `,
	    props: [
		'p'
	    ]
        };


  createApp({
    data() {
      return {
	apis: APIS 
      }
    },
    components: {
        'FormParam': FormParam 
    }
  }).mount('#app')
function sendJSON(event) {
    event.preventDefault();

     const formElements = event.target.elements;
     const data = {};

      Array.from(formElements).forEach(element => {
        if (element.name) {
          if (element.type === 'checkbox') {
            data[element.name] = element.checked;
          } else if (element.type === 'number') {
            data[element.name] = element.value ? Number(element.value) : null;
          } else {
            data[element.name] = element.value;
          }
        }
      });

    fetch(event.target.action, {
	method: 'POST',
	headers: {
	    'Content-Type': 'application/json'
	},
	body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
	console.log('Success:', data);
	alert(JSON.stringify(data, null, 2));
    })
    .catch((error) => {
	console.error('Error:', error);
	alert('Error submitting form');
    });
}
</script>
</body>
</html>
"""
