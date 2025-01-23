# Filter database entries

When you [query a database](https://developers.notion.com/reference/post-database-query), you can send a `<span class="cm-s-neo" data-testid="SyntaxHighlighter">filter</span>` object in the body of the request that limits the returned entries based on the specified criteria.

For example, the below query limits the response to entries where the `<span class="cm-s-neo" data-testid="SyntaxHighlighter">"Task completed"</span>` `<span class="cm-s-neo" data-testid="SyntaxHighlighter">checkbox</span>` property value is `<span class="cm-s-neo" data-testid="SyntaxHighlighter">true</span>`:

cURL

<pre><button aria-label="Copy Code" class="rdmd-code-copy fa"></button><code class="rdmd-code lang-curl theme-light" data-lang="curl" name="" tabindex="0"><div class="cm-s-neo" data-testid="SyntaxHighlighter"><span class="cm-builtin">curl</span> <span class="cm-attribute">-X</span> POST <span class="cm-string">'https://api.notion.com/v1/databases/897e5a76ae524b489fdfe71f5945d1af/query'</span> \
  <span class="cm-attribute">-H</span> <span class="cm-string">'Authorization: Bearer '"</span><span class="cm-def">$NOTION_API_KEY</span><span class="cm-string">"''</span> \
  <span class="cm-attribute">-H</span> <span class="cm-string">'Notion-Version: 2022-06-28'</span> \
  <span class="cm-attribute">-H</span> <span class="cm-string">"Content-Type: application/json"</span> \
<span class="cm-attribute">--data</span> <span class="cm-string">'{</span>
<span class="cm-string">  "filter": {</span>
<span class="cm-string">    "property": "Task completed",</span>
<span class="cm-string">    "checkbox": {</span>
<span class="cm-string">        "equals": true</span>
<span class="cm-string">   }</span>
<span class="cm-string">  }</span>
<span class="cm-string">}'</span>
</div></code></pre>

Here is the same query using the [Notion SDK for JavaScript](https://github.com/makenotion/notion-sdk-js):

JavaScript

<pre><button aria-label="Copy Code" class="rdmd-code-copy fa"></button><code class="rdmd-code lang-javascript theme-light" data-lang="javascript" name="" tabindex="0"><div class="cm-s-neo" data-testid="SyntaxHighlighter"><span class="cm-keyword">const</span> { <span class="cm-def">Client</span> } <span class="cm-operator">=</span> <span class="cm-variable">require</span>(<span class="cm-string">'@notionhq/client'</span>);

<span class="cm-keyword">const</span> <span class="cm-def">notion</span> <span class="cm-operator">=</span> <span class="cm-keyword">new</span> <span class="cm-variable">Client</span>({ <span class="cm-property">auth</span>: <span class="cm-variable">process</span>.<span class="cm-property">env</span>.<span class="cm-property">NOTION_API_KEY</span> });
<span class="cm-comment">// replace with your own database ID</span>
<span class="cm-keyword">const</span> <span class="cm-def">databaseId</span> <span class="cm-operator">=</span> <span class="cm-string">'d9824bdc-8445-4327-be8b-5b47500af6ce'</span>;

<span class="cm-keyword">const</span> <span class="cm-def">filteredRows</span> <span class="cm-operator">=</span> <span class="cm-keyword">async</span> () <span class="cm-operator">=></span> {
	<span class="cm-keyword">const</span> <span class="cm-def">response</span> <span class="cm-operator">=</span> <span class="cm-keyword">await</span> <span class="cm-variable">notion</span>.<span class="cm-property">databases</span>.<span class="cm-property">query</span>({
	  <span class="cm-property">database_id</span>: <span class="cm-variable">databaseId</span>,
	  <span class="cm-property">filter</span>: {
	    <span class="cm-property">property</span>: <span class="cm-string">"Task completed"</span>,
	    <span class="cm-property">checkbox</span>: {
	      <span class="cm-property">equals</span>: <span class="cm-atom">true</span>
	    }
	  },
	});
  <span class="cm-keyword">return</span> <span class="cm-variable-2">response</span>;
}

</div></code></pre>

Filters can be chained with the `<span class="cm-s-neo" data-testid="SyntaxHighlighter">and</span>` and `<span class="cm-s-neo" data-testid="SyntaxHighlighter">or</span>` keys so that multiple filters are applied at the same time. (See [Query a database](https://developers.notion.com/reference/post-database-query) for additional examples.)

JSON

<pre><button aria-label="Copy Code" class="rdmd-code-copy fa"></button><code class="rdmd-code lang-json theme-light" data-lang="json" name="" tabindex="0"><div class="cm-s-neo" data-testid="SyntaxHighlighter">{
  <span class="cm-property">"and"</span>: [
    {
      <span class="cm-property">"property"</span>: <span class="cm-string">"Done"</span>,
      <span class="cm-property">"checkbox"</span>: {
        <span class="cm-property">"equals"</span>: <span class="cm-atom">true</span>
      }
    }, 
    {
      <span class="cm-property">"or"</span>: [
        {
          <span class="cm-property">"property"</span>: <span class="cm-string">"Tags"</span>,
          <span class="cm-property">"contains"</span>: <span class="cm-string">"A"</span>
        },
        {
          <span class="cm-property">"property"</span>: <span class="cm-string">"Tags"</span>,
          <span class="cm-property">"contains"</span>: <span class="cm-string">"B"</span>
        }
      ]
    }
  ]
}
</div></code></pre>

If no filter is provided, all the pages in the database will be returned with pagination.

## 

The filter object

Each `<span class="cm-s-neo" data-testid="SyntaxHighlighter">filter</span>` object contains the following fields:


| Field                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | Type                                                                   | Description                                                                                                                                                                                                                                                                                                              | Example value                                                                                  |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------- |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">property</span>`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>` | The name of the property as it appears in the database, or the property ID.                                                                                                                                                                                                                                              | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">"Task completed"</span>`               |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">checkbox</span>`<br/>`<span class="cm-s-neo" data-testid="SyntaxHighlighter">date</span>`<br/>`<span class="cm-s-neo" data-testid="SyntaxHighlighter">files</span>`<br/>`<span class="cm-s-neo" data-testid="SyntaxHighlighter">formula</span>`<br/>`<span class="cm-s-neo" data-testid="SyntaxHighlighter">multi_select</span>`<br/>`<span class="cm-s-neo" data-testid="SyntaxHighlighter">number</span>`<br/>`<span class="cm-s-neo" data-testid="SyntaxHighlighter">people</span>`<br/>`<span class="cm-s-neo" data-testid="SyntaxHighlighter">phone_number</span>`<br/>`<span class="cm-s-neo" data-testid="SyntaxHighlighter">relation</span>`<br/>`<span class="cm-s-neo" data-testid="SyntaxHighlighter">rich_text</span>`<br/>`<span class="cm-s-neo" data-testid="SyntaxHighlighter">select</span>`<br/>`<span class="cm-s-neo" data-testid="SyntaxHighlighter">status</span>`<br/>`<span class="cm-s-neo" data-testid="SyntaxHighlighter">timestamp</span>`<br/>`<span class="cm-s-neo" data-testid="SyntaxHighlighter">ID</span>` | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">object</span>` | The type-specific filter condition for the query. Only types listed in the Field column of this table are supported.<br/><br/>Refer to [type-specific filter conditions](https://developers.notion.com/reference/post-database-query-filter#type-specific-filter-conditions) for details on corresponding object values. | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">"checkbox": { "equals": true }</span>` |

Example checkbox filter object

<pre><button aria-label="Copy Code" class="rdmd-code-copy fa"></button><code class="rdmd-code lang-json theme-light" data-lang="json" name="Example checkbox filter object" tabindex="0"><div class="cm-s-neo" data-testid="SyntaxHighlighter">{
  <span class="cm-property">"filter"</span>: {
    <span class="cm-property">"property"</span>: <span class="cm-string">"Task completed"</span>,
    <span class="cm-property">"checkbox"</span>: {
      <span class="cm-property">"equals"</span>: <span class="cm-atom">true</span>
    }
  }
}
</div></code></pre>

> ## 👍
>
> The filter object mimics the database [filter option in the Notion UI](https://www.notion.so/help/views-filters-and-sorts).

## 

Type-specific filter conditions

### 

Checkbox


| Field                                                                          | Type                                                                    | Description                                                                                                                                                                                                       | Example value                                                         |
| ------------------------------------------------------------------------------ | ----------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">equals</span>`         | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">boolean</span>` | Whether a`<span class="cm-s-neo" data-testid="SyntaxHighlighter">checkbox</span>` property value matches the provided value exactly.<br/><br/>Returns or excludes all database entries with an exact value match. | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">false</span>` |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">does_not_equal</span>` | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">boolean</span>` | Whether a`<span class="cm-s-neo" data-testid="SyntaxHighlighter">checkbox</span>` property value differs from the provided value.<br/><br/>Returns or excludes all database entries with a difference in values.  | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">true</span>`  |

Example checkbox filter condition

<pre><button aria-label="Copy Code" class="rdmd-code-copy fa"></button><code class="rdmd-code lang-json theme-light" data-lang="json" name="Example checkbox filter condition" tabindex="0"><div class="cm-s-neo" data-testid="SyntaxHighlighter">{
  <span class="cm-property">"filter"</span>: {
    <span class="cm-property">"property"</span>: <span class="cm-string">"Task completed"</span>,
    <span class="cm-property">"checkbox"</span>: {
      <span class="cm-property">"does_not_equal"</span>: <span class="cm-atom">true</span>
    }
  }
}
</div></code></pre>

### 

Date

> ## 📘
>
> For the `<span class="cm-s-neo" data-testid="SyntaxHighlighter">after</span>`, `<span class="cm-s-neo" data-testid="SyntaxHighlighter">before</span>`, `<span class="cm-s-neo" data-testid="SyntaxHighlighter">equals, on_or_before</span>`, and `<span class="cm-s-neo" data-testid="SyntaxHighlighter">on_or_after</span>` fields, if a date string with a time is provided, then the comparison is done with millisecond precision.
>
> If no timezone is provided, then the timezone defaults to UTC.

A date filter condition can be used to limit `<span class="cm-s-neo" data-testid="SyntaxHighlighter">date</span>` property value types and the [timestamp](https://developers.notion.com/reference/post-database-query-filter#timestamp) property types `<span class="cm-s-neo" data-testid="SyntaxHighlighter">created_time</span>` and `<span class="cm-s-neo" data-testid="SyntaxHighlighter">last_edited_time</span>`.

The condition contains the below fields:


| Field                                                                        | Type                                                                                                                             | Description                                                                                                                                                                 | Example value                                                                                                                                                                                                                                                                    |
| ---------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">after</span>`        | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>` ([ISO 8601 date](https://en.wikipedia.org/wiki/ISO_8601)) | The value to compare the date property value against.<br/><br/>Returns database entries where the date property value is after the provided date.                           | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">"2021-05-10"</span>`<br/><br/>`<span class="cm-s-neo" data-testid="SyntaxHighlighter">"2021-05-10T12:00:00"</span>`<br/><br/>`<span class="cm-s-neo" data-testid="SyntaxHighlighter">"2021-10-15T12:00:00-07:00"</span>` |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">before</span>`       | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>` ([ISO 8601 date](https://en.wikipedia.org/wiki/ISO_8601)) | The value to compare the date property value against.<br/><br/>Returns database entries where the date property value is before the provided date.                          | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">"2021-05-10"</span>`<br/><br/>`<span class="cm-s-neo" data-testid="SyntaxHighlighter">"2021-05-10T12:00:00"</span>`<br/><br/>`<span class="cm-s-neo" data-testid="SyntaxHighlighter">"2021-10-15T12:00:00-07:00"</span>` |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">equals</span>`       | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>` ([ISO 8601 date](https://en.wikipedia.org/wiki/ISO_8601)) | The value to compare the date property value against.<br/><br/>Returns database entries where the date property value is the provided date.                                 | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">"2021-05-10"</span>`<br/><br/>`<span class="cm-s-neo" data-testid="SyntaxHighlighter">"2021-05-10T12:00:00"</span>`<br/><br/>`<span class="cm-s-neo" data-testid="SyntaxHighlighter">"2021-10-15T12:00:00-07:00"</span>` |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">is_empty</span>`     | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">true</span>`                                                             | The value to compare the date property value against.<br/><br/>Returns database entries where the date property value contains no data.                                     | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">true</span>`                                                                                                                                                                                                             |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">is_not_empty</span>` | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">true</span>`                                                             | The value to compare the date property value against.<br/><br/>Returns database entries where the date property value is not empty.                                         | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">true</span>`                                                                                                                                                                                                             |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">next_month</span>`   | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">object</span>` (empty)                                                   | A filter that limits the results to database entries where the date property value is within the next month.                                                                | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">{}</span>`                                                                                                                                                                                                               |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">next_week</span>`    | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">object</span>` (empty)                                                   | A filter that limits the results to database entries where the date property value is within the next week.                                                                 | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">{}</span>`                                                                                                                                                                                                               |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">next_year</span>`    | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">object</span>` (empty)                                                   | A filter that limits the results to database entries where the date property value is within the next year.                                                                 | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">{}</span>`                                                                                                                                                                                                               |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">on_or_after</span>`  | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>` ([ISO 8601 date](https://en.wikipedia.org/wiki/ISO_8601)) | The value to compare the date property value against.<br/><br/>Returns database entries where the date property value is on or after the provided date.                     | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">"2021-05-10"</span>`<br/><br/>`<span class="cm-s-neo" data-testid="SyntaxHighlighter">"2021-05-10T12:00:00"</span>`<br/><br/>`<span class="cm-s-neo" data-testid="SyntaxHighlighter">"2021-10-15T12:00:00-07:00"</span>` |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">on_or_before</span>` | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>` ([ISO 8601 date](https://en.wikipedia.org/wiki/ISO_8601)) | The value to compare the date property value against.<br/><br/>Returns database entries where the date property value is on or before the provided date.                    | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">"2021-05-10"</span>`<br/><br/>`<span class="cm-s-neo" data-testid="SyntaxHighlighter">"2021-05-10T12:00:00"</span>`<br/><br/>`<span class="cm-s-neo" data-testid="SyntaxHighlighter">"2021-10-15T12:00:00-07:00"</span>` |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">past_month</span>`   | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">object</span>` (empty)                                                   | A filter that limits the results to database entries where the`<span class="cm-s-neo" data-testid="SyntaxHighlighter">date</span>` property value is within the past month. | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">{}</span>`                                                                                                                                                                                                               |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">past_week</span>`    | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">object</span>` (empty)                                                   | A filter that limits the results to database entries where the`<span class="cm-s-neo" data-testid="SyntaxHighlighter">date</span>` property value is within the past week.  | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">{}</span>`                                                                                                                                                                                                               |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">past_year</span>`    | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">object</span>` (empty)                                                   | A filter that limits the results to database entries where the`<span class="cm-s-neo" data-testid="SyntaxHighlighter">date</span>` property value is within the past year.  | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">{}</span>`                                                                                                                                                                                                               |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">this_week</span>`    | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">object</span>` (empty)                                                   | A filter that limits the results to database entries where the`<span class="cm-s-neo" data-testid="SyntaxHighlighter">date</span>` property value is this week.             | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">{}</span>`                                                                                                                                                                                                               |

Example date filter condition

<pre><button aria-label="Copy Code" class="rdmd-code-copy fa"></button><code class="rdmd-code lang-json theme-light" data-lang="json" name="Example date filter condition" tabindex="0"><div class="cm-s-neo" data-testid="SyntaxHighlighter">{
  <span class="cm-property">"filter"</span>: {
    <span class="cm-property">"property"</span>: <span class="cm-string">"Due date"</span>,
    <span class="cm-property">"date"</span>: {
      <span class="cm-property">"on_or_after"</span>: <span class="cm-string">"2023-02-08"</span>
    }
  }
}
</div></code></pre>

### 

Files


| Field                                                                        | Type                                                                 | Description                                                                                                                                                                                                                                        | Example value                                                        |
| ---------------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">is_empty</span>`     | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">true</span>` | Whether the files property value does not contain any data.<br/><br/>Returns all database entries with an empty `<span class="cm-s-neo" data-testid="SyntaxHighlighter">files</span>` property value.                                              | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">true</span>` |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">is_not_empty</span>` | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">true</span>` | Whether the`<span class="cm-s-neo" data-testid="SyntaxHighlighter">files</span>` property value contains data.<br/><br/>Returns all entries with a populated `<span class="cm-s-neo" data-testid="SyntaxHighlighter">files</span>` property value. | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">true</span>` |

Example files filter condition

<pre><button aria-label="Copy Code" class="rdmd-code-copy fa"></button><code class="rdmd-code lang-json theme-light" data-lang="json" name="Example files filter condition" tabindex="0"><div class="cm-s-neo" data-testid="SyntaxHighlighter">{
  <span class="cm-property">"filter"</span>: {
    <span class="cm-property">"property"</span>: <span class="cm-string">"Blueprint"</span>,
    <span class="cm-property">"files"</span>: {
      <span class="cm-property">"is_not_empty"</span>: <span class="cm-atom">true</span>
    }
  }
}
</div></code></pre>

### 

Formula

The primary field of the `<span class="cm-s-neo" data-testid="SyntaxHighlighter">formula</span>` filter condition object matches the type of the formula’s result. For example, to filter a formula property that computes a `<span class="cm-s-neo" data-testid="SyntaxHighlighter">checkbox</span>`, use a `<span class="cm-s-neo" data-testid="SyntaxHighlighter">formula</span>` filter condition object with a `<span class="cm-s-neo" data-testid="SyntaxHighlighter">checkbox</span>` field containing a checkbox filter condition as its value.


| Field                                                                    | Type                                                                   | Description                                                                                                                                                                                                                                   | Example value                                                                                                           |
| ------------------------------------------------------------------------ | ---------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">checkbox</span>` | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">object</span>` | A[checkbox](https://developers.notion.com/reference/post-database-query-filter#checkbox) filter condition to compare the formula result against.<br/><br/>Returns database entries where the formula result matches the provided condition.   | Refer to the[checkbox](https://developers.notion.com/reference/post-database-query-filter#checkbox) filter condition.   |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">date</span>`     | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">object</span>` | A[date](https://developers.notion.com/reference/post-database-query-filter#date) filter condition to compare the formula result against.<br/><br/>Returns database entries where the formula result matches the provided condition.           | Refer to the[date](https://developers.notion.com/reference/post-database-query-filter#date) filter condition.           |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">number</span>`   | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">object</span>` | A[number](https://developers.notion.com/reference/post-database-query-filter#number) filter condition to compare the formula result against.<br/><br/>Returns database entries where the formula result matches the provided condition.       | Refer to the[number](https://developers.notion.com/reference/post-database-query-filter#number) filter condition.       |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>`   | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">object</span>` | A[rich text](https://developers.notion.com/reference/post-database-query-filter#rich-text) filter condition to compare the formula result against.<br/><br/>Returns database entries where the formula result matches the provided condition. | Refer to the[rich text](https://developers.notion.com/reference/post-database-query-filter#rich-text) filter condition. |

Example formula filter condition

<pre><button aria-label="Copy Code" class="rdmd-code-copy fa"></button><code class="rdmd-code lang-json theme-light" data-lang="json" name="Example formula filter condition" tabindex="0"><div class="cm-s-neo" data-testid="SyntaxHighlighter">{
  <span class="cm-property">"filter"</span>: {
    <span class="cm-property">"property"</span>: <span class="cm-string">"One month deadline"</span>,
    <span class="cm-property">"formula"</span>: {
      <span class="cm-property">"date"</span>:{
          <span class="cm-property">"after"</span>: <span class="cm-string">"2021-05-10"</span>
      }
    }
  }
}
</div></code></pre>

### 

Multi-select


| Field                                                                            | Type                                                                   | Description                                                                                                                                                      | Example value                                                                 |
| -------------------------------------------------------------------------------- | ---------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">contains</span>`         | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>` | The value to compare the multi-select property value against.<br/><br/>Returns database entries where the multi-select value matches the provided string.        | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">"Marketing"</span>`   |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">does_not_contain</span>` | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>` | The value to compare the multi-select property value against.<br/><br/>Returns database entries where the multi-select value does not match the provided string. | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">"Engineering"</span>` |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">is_empty</span>`         | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">true</span>`   | Whether the multi-select property value is empty.<br/><br/>Returns database entries where the multi-select value does not contain any data.                      | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">true</span>`          |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">is_not_empty</span>`     | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">true</span>`   | Whether the multi-select property value is not empty.<br/><br/>Returns database entries where the multi-select value does contains data.                         | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">true</span>`          |

Example multi-select filter condition

<pre><button aria-label="Copy Code" class="rdmd-code-copy fa"></button><code class="rdmd-code lang-json theme-light" data-lang="json" name="Example multi-select filter condition" tabindex="0"><div class="cm-s-neo" data-testid="SyntaxHighlighter">{
  <span class="cm-property">"filter"</span>: {
    <span class="cm-property">"property"</span>: <span class="cm-string">"Programming language"</span>,
    <span class="cm-property">"multi_select"</span>: {
      <span class="cm-property">"contains"</span>: <span class="cm-string">"TypeScript"</span>
    }
  }
}
</div></code></pre>

### 

Number


| Field                                                                                    | Type                                                                   | Description                                                                                                                                                                                                                                                                                                | Example value                                                        |
| ---------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">does_not_equal</span>`           | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">number</span>` | The`<span class="cm-s-neo" data-testid="SyntaxHighlighter">number</span>` to compare the number property value against.<br/><br/>Returns database entries where the number property value differs from the provided `<span class="cm-s-neo" data-testid="SyntaxHighlighter">number</span>`.                | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">42</span>`   |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">equals</span>`                   | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">number</span>` | The`<span class="cm-s-neo" data-testid="SyntaxHighlighter">number</span>` to compare the number property value against.<br/><br/>Returns database entries where the number property value is the same as the provided number.                                                                              | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">42</span>`   |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">greater_than</span>`             | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">number</span>` | The`<span class="cm-s-neo" data-testid="SyntaxHighlighter">number</span>` to compare the number property value against.<br/><br/>Returns database entries where the number property value exceeds the provided `<span class="cm-s-neo" data-testid="SyntaxHighlighter">number</span>`.                     | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">42</span>`   |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">greater_than_or_equal_to</span>` | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">number</span>` | The`<span class="cm-s-neo" data-testid="SyntaxHighlighter">number</span>` to compare the number property value against.<br/><br/>Returns database entries where the number property value is equal to or exceeds the provided `<span class="cm-s-neo" data-testid="SyntaxHighlighter">number</span>`.      | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">42</span>`   |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">is_empty</span>`                 | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">true</span>`   | Whether the`<span class="cm-s-neo" data-testid="SyntaxHighlighter">number</span>` property value is empty.<br/><br/>Returns database entries where the number property value does not contain any data.                                                                                                    | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">true</span>` |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">is_not_empty</span>`             | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">true</span>`   | Whether the number property value is not empty.<br/><br/>Returns database entries where the number property value contains data.                                                                                                                                                                           | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">true</span>` |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">less_than</span>`                | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">number</span>` | The`<span class="cm-s-neo" data-testid="SyntaxHighlighter">number</span>` to compare the number property value against.<br/><br/>Returns database entries where the number property value is less than the provided `<span class="cm-s-neo" data-testid="SyntaxHighlighter">number</span>`.                | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">42</span>`   |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">less_than_or_equal_to</span>`    | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">number</span>` | The`<span class="cm-s-neo" data-testid="SyntaxHighlighter">number</span>` to compare the number property value against.<br/><br/>Returns database entries where the number property value is equal to or is less than the provided `<span class="cm-s-neo" data-testid="SyntaxHighlighter">number</span>`. | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">42</span>`   |

Example number filter condition

<pre><button aria-label="Copy Code" class="rdmd-code-copy fa"></button><code class="rdmd-code lang-json theme-light" data-lang="json" name="Example number filter condition" tabindex="0"><div class="cm-s-neo" data-testid="SyntaxHighlighter">{
  <span class="cm-property">"filter"</span>: {
    <span class="cm-property">"property"</span>: <span class="cm-string">"Estimated working days"</span>,
    <span class="cm-property">"number"</span>: {
      <span class="cm-property">"less_than_or_equal_to"</span>: <span class="cm-number">5</span>
    }
  }
}
</div></code></pre>

### 

People

You can apply a people filter condition to `<span class="cm-s-neo" data-testid="SyntaxHighlighter">people</span>`, `<span class="cm-s-neo" data-testid="SyntaxHighlighter">created_by</span>`, and `<span class="cm-s-neo" data-testid="SyntaxHighlighter">last_edited_by</span>` database property types.

The people filter condition contains the following fields:


| Field                                                                            | Type                                                                            | Description                                                                                                                                                                                                                     | Example value                                                                                          |
| -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">contains</span>`         | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>` (UUIDv4) | The value to compare the people property value against.<br/><br/>Returns database entries where the people property value contains the provided `<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>`.         | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">"6c574cee-ca68-41c8-86e0-1b9e992689fb"</span>` |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">does_not_contain</span>` | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>` (UUIDv4) | The value to compare the people property value against.<br/><br/>Returns database entries where the people property value does not contain the provided `<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>`. | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">"6c574cee-ca68-41c8-86e0-1b9e992689fb"</span>` |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">is_empty</span>`         | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">true</span>`            | Whether the people property value does not contain any data.<br/><br/>Returns database entries where the people property value does not contain any data.                                                                       | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">true</span>`                                   |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">is_not_empty</span>`     | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">true</span>`            | Whether the people property value contains data.<br/><br/>Returns database entries where the people property value is not empty.                                                                                                | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">true</span>`                                   |

Example people filter condition

<pre><button aria-label="Copy Code" class="rdmd-code-copy fa"></button><code class="rdmd-code lang-json theme-light" data-lang="json" name="Example people filter condition" tabindex="0"><div class="cm-s-neo" data-testid="SyntaxHighlighter">{
  <span class="cm-property">"filter"</span>: {
    <span class="cm-property">"property"</span>: <span class="cm-string">"Last edited by"</span>,
    <span class="cm-property">"people"</span>: {
      <span class="cm-property">"contains"</span>: <span class="cm-string">"c2f20311-9e54-4d11-8c79-7398424ae41e"</span>
    }
  }
}
</div></code></pre>

### 

Relation


| Field                                                                            | Type                                                                            | Description                                                                                                                                                                                                                 | Example value                                                                                          |
| -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">contains</span>`         | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>` (UUIDv4) | The value to compare the relation property value against.<br/><br/>Returns database entries where the relation property value contains the provided `<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>`. | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">"6c574cee-ca68-41c8-86e0-1b9e992689fb"</span>` |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">does_not_contain</span>` | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>` (UUIDv4) | The value to compare the relation property value against.<br/><br/>Returns entries where the relation property value does not contain the provided `<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>`.  | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">"6c574cee-ca68-41c8-86e0-1b9e992689fb"</span>` |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">is_empty</span>`         | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">true</span>`            | Whether the relation property value does not contain data.<br/><br/>Returns database entries where the relation property value does not contain any data.                                                                   | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">true</span>`                                   |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">is_not_empty</span>`     | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">true</span>`            | Whether the relation property value contains data.<br/><br/>Returns database entries where the property value is not empty.                                                                                                 | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">true</span>`                                   |

Example relation filter condition

<pre><button aria-label="Copy Code" class="rdmd-code-copy fa"></button><code class="rdmd-code lang-json theme-light" data-lang="json" name="Example relation filter condition" tabindex="0"><div class="cm-s-neo" data-testid="SyntaxHighlighter">{
  <span class="cm-property">"filter"</span>: {
    <span class="cm-property">"property"</span>: <span class="cm-string">"✔️ Task List"</span>,
    <span class="cm-property">"relation"</span>: {
      <span class="cm-property">"contains"</span>: <span class="cm-string">"0c1f7cb280904f18924ed92965055e32"</span>
    }
  }
}
</div></code></pre>

### 

Rich text


| Field                                                                            | Type                                                                   | Description                                                                                                                                                                                                                                                                                   | Example value                                                                 |
| -------------------------------------------------------------------------------- | ---------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">contains</span>`         | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>` | The`<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>` to compare the text property value against.<br/><br/>Returns database entries with a text property value that includes the provided `<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>`.         | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">"Moved to Q2"</span>` |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">does_not_contain</span>` | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>` | The`<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>` to compare the text property value against.<br/><br/>Returns database entries with a text property value that does not include the provided `<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>`. | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">"Moved to Q2"</span>` |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">does_not_equal</span>`   | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>` | The`<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>` to compare the text property value against.<br/><br/>Returns database entries with a text property value that does not match the provided `<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>`.   | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">"Moved to Q2"</span>` |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">ends_with</span>`        | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>` | The`<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>` to compare the text property value against.<br/><br/>Returns database entries with a text property value that ends with the provided `<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>`.        | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">"Q2"</span>`          |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">equals</span>`           | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>` | The`<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>` to compare the text property value against.<br/><br/>Returns database entries with a text property value that matches the provided `<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>`.          | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">"Moved to Q2"</span>` |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">is_empty</span>`         | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">true</span>`   | Whether the text property value does not contain any data.<br/><br/>Returns database entries with a text property value that is empty.                                                                                                                                                        | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">true</span>`          |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">is_not_empty</span>`     | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">true</span>`   | Whether the text property value contains any data.<br/><br/>Returns database entries with a text property value that contains data.                                                                                                                                                           | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">true</span>`          |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">starts_with</span>`      | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>` | The`<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>` to compare the text property value against.<br/><br/>Returns database entries with a text property value that starts with the provided `<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>`.      | "Moved"                                                                       |

Example rich text filter condition

<pre><button aria-label="Copy Code" class="rdmd-code-copy fa"></button><code class="rdmd-code lang-json theme-light" data-lang="json" name="Example rich text filter condition" tabindex="0"><div class="cm-s-neo" data-testid="SyntaxHighlighter">{
  <span class="cm-property">"filter"</span>: {
    <span class="cm-property">"property"</span>: <span class="cm-string">"Description"</span>,
    <span class="cm-property">"rich_text"</span>: {
      <span class="cm-property">"contains"</span>: <span class="cm-string">"cross-team"</span>
    }
  }
}
</div></code></pre>

### 

Rollup

A rollup database property can evaluate to an array, date, or number value. The filter condition for the rollup property contains a `<span class="cm-s-neo" data-testid="SyntaxHighlighter">rollup</span>` key and a corresponding object value that depends on the computed value type.

#### 

Filter conditions for `<span class="cm-s-neo" data-testid="SyntaxHighlighter">array</span>` rollup values


| Field                                                                 | Type                                                                   | Description                                                                                                                                                                                                                                                                                                    | Example value                                                                                                     |
| --------------------------------------------------------------------- | ---------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">any</span>`   | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">object</span>` | The value to compare each rollup property value against. Can be a[filter condition](https://developers.notion.com/reference/post-database-query-filter#type-specific-filter-conditions) for any other type.<br/><br/>Returns database entries where the rollup property value matches the provided criteria.   | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">"rich_text": { "contains": "Take Fig on a walk" }</span>` |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">every</span>` | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">object</span>` | The value to compare each rollup property value against. Can be a[filter condition](https://developers.notion.com/reference/post-database-query-filter#type-specific-filter-conditions) for any other type.<br/><br/>Returns database entries where every rollup property value matches the provided criteria. | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">"rich_text": { "contains": "Take Fig on a walk" }</span>` |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">none</span>`  | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">object</span>` | The value to compare each rollup property value against. Can be a[filter condition](https://developers.notion.com/reference/post-database-query-filter#type-specific-filter-conditions) for any other type.<br/><br/>Returns database entries where no rollup property value matches the provided criteria.    | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">"rich_text": { "contains": "Take Fig on a walk" }</span>` |

Example array rollup filter condition

<pre><button aria-label="Copy Code" class="rdmd-code-copy fa"></button><code class="rdmd-code lang-json theme-light" data-lang="json" name="Example array rollup filter condition" tabindex="0"><div class="cm-s-neo" data-testid="SyntaxHighlighter">{
  <span class="cm-property">"filter"</span>: {
    <span class="cm-property">"property"</span>: <span class="cm-string">"Related tasks"</span>,
    <span class="cm-property">"rollup"</span>: {
      <span class="cm-property">"any"</span>: {
        <span class="cm-property">"rich_text"</span>: {
          <span class="cm-property">"contains"</span>: <span class="cm-string">"Migrate database"</span>
        }
      }
    }
  }
}
</div></code></pre>

#### 

Filter conditions for `<span class="cm-s-neo" data-testid="SyntaxHighlighter">date</span>` rollup values

A rollup value is stored as a `<span class="cm-s-neo" data-testid="SyntaxHighlighter">date</span>` only if the "Earliest date", "Latest date", or "Date range" computation is selected for the property in the Notion UI.


| Field                                                                | Type                                                                   | Description                                                                                                                                                                                                                     | Example value                                                                                                 |
| -------------------------------------------------------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">date</span>` | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">object</span>` | A[date](https://developers.notion.com/reference/post-database-query-filter#date) filter condition to compare the rollup value against.<br/><br/>Returns database entries where the rollup value matches the provided condition. | Refer to the[date](https://developers.notion.com/reference/post-database-query-filter#date) filter condition. |

Example date rollup filter condition

<pre><button aria-label="Copy Code" class="rdmd-code-copy fa"></button><code class="rdmd-code lang-json theme-light" data-lang="json" name="Example date rollup filter condition" tabindex="0"><div class="cm-s-neo" data-testid="SyntaxHighlighter">{
  <span class="cm-property">"filter"</span>: {
    <span class="cm-property">"property"</span>: <span class="cm-string">"Parent project due date"</span>,
    <span class="cm-property">"rollup"</span>: {
      <span class="cm-property">"date"</span>: {
        <span class="cm-property">"on_or_before"</span>: <span class="cm-string">"2023-02-08"</span>
      }
    }
  }
}
</div></code></pre>

#### 

Filter conditions for `<span class="cm-s-neo" data-testid="SyntaxHighlighter">number</span>` rollup values


| Field                                                                  | Type                                                                   | Description                                                                                                                                                                                                                         | Example value                                                                                                     |
| ---------------------------------------------------------------------- | ---------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">number</span>` | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">object</span>` | A[number](https://developers.notion.com/reference/post-database-query-filter#number) filter condition to compare the rollup value against.<br/><br/>Returns database entries where the rollup value matches the provided condition. | Refer to the[number](https://developers.notion.com/reference/post-database-query-filter#number) filter condition. |

Example number rollup filter condition

<pre><button aria-label="Copy Code" class="rdmd-code-copy fa"></button><code class="rdmd-code lang-json theme-light" data-lang="json" name="Example number rollup filter condition" tabindex="0"><div class="cm-s-neo" data-testid="SyntaxHighlighter">{
  <span class="cm-property">"filter"</span>: {
    <span class="cm-property">"property"</span>: <span class="cm-string">"Total estimated working days"</span>,
    <span class="cm-property">"rollup"</span>: {
      <span class="cm-property">"number"</span>: {
        <span class="cm-property">"does_not_equal"</span>: <span class="cm-number">42</span>
      }
    }
  }
}
</div></code></pre>

### 

Select


| Field                                                                          | Type                                                                   | Description                                                                                                                                                                                                                                                                                   | Example value                                                               |
| ------------------------------------------------------------------------------ | ---------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">equals</span>`         | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>` | The`<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>` to compare the select property value against.<br/><br/>Returns database entries where the select property value matches the provided string.                                                                        | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">"This week"</span>` |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">does_not_equal</span>` | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>` | The`<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>` to compare the select property value against.<br/><br/>Returns database entries where the select property value does not match the provided `<span class="cm-s-neo" data-testid="SyntaxHighlighter">string</span>`. | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">"Backlog"</span>`   |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">is_empty</span>`       | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">true</span>`   | Whether the select property value does not contain data.<br/><br/>Returns database entries where the select property value is empty.                                                                                                                                                          | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">true</span>`        |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">is_not_empty</span>`   | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">true</span>`   | Whether the select property value contains data.<br/><br/>Returns database entries where the select property value is not empty.                                                                                                                                                              | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">true</span>`        |

Example select filter condition

<pre><button aria-label="Copy Code" class="rdmd-code-copy fa"></button><code class="rdmd-code lang-json theme-light" data-lang="json" name="Example select filter condition" tabindex="0"><div class="cm-s-neo" data-testid="SyntaxHighlighter">{
  <span class="cm-property">"filter"</span>: {
    <span class="cm-property">"property"</span>: <span class="cm-string">"Frontend framework"</span>,
    <span class="cm-property">"select"</span>: {
      <span class="cm-property">"equals"</span>: <span class="cm-string">"React"</span>
    }
  }
}
</div></code></pre>

### 

Status


| Field            | Type   | Description                                                                                                                                                    | Example value |
| ---------------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- |
| equals           | string | The string to compare the status property value against.<br/><br/>Returns database entries where the status property value matches the provided string.        | "This week"   |
| does\_not\_equal | string | The string to compare the status property value against.<br/><br/>Returns database entries where the status property value does not match the provided string. | "Backlog"     |
| is\_empty        | true   | Whether the status property value does not contain data.<br/><br/>Returns database entries where the status property value is empty.                           | true          |
| is\_not\_empty   | true   | Whether the status property value contains data.<br/><br/>Returns database entries where the status property value is not empty.                               | true          |

Example status filter condition

<pre><button aria-label="Copy Code" class="rdmd-code-copy fa"></button><code class="rdmd-code lang-json theme-light" data-lang="json" name="Example status filter condition" tabindex="0"><div class="cm-s-neo" data-testid="SyntaxHighlighter">{
  <span class="cm-property">"filter"</span>: {
    <span class="cm-property">"property"</span>: <span class="cm-string">"Project status"</span>,
    <span class="cm-property">"status"</span>: {
      <span class="cm-property">"equals"</span>: <span class="cm-string">"Not started"</span>
    }
  }
}
</div></code></pre>

### 

Timestamp

Use a timestamp filter condition to filter results based on `<span class="cm-s-neo" data-testid="SyntaxHighlighter">created_time</span>` or `<span class="cm-s-neo" data-testid="SyntaxHighlighter">last_edited_time</span>` values.


| Field                                | Type                             | Description                                                              | Example value                                                                                                 |
| ------------------------------------ | -------------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------- |
| timestamp                            | created\_time last\_edited\_time | A constant string representing the type of timestamp to use as a filter. | "created\_time"                                                                                               |
| created\_time<br/>last\_edited\_time | object                           | A date filter condition used to filter the specified timestamp.          | Refer to the[date](https://developers.notion.com/reference/post-database-query-filter#date) filter condition. |

Example timestamp filter condition for created\_time

<pre><button aria-label="Copy Code" class="rdmd-code-copy fa"></button><code class="rdmd-code lang-json theme-light" data-lang="json" name="Example timestamp filter condition for created_time" tabindex="0"><div class="cm-s-neo" data-testid="SyntaxHighlighter">{
  <span class="cm-property">"filter"</span>: {
    <span class="cm-property">"timestamp"</span>: <span class="cm-string">"created_time"</span>,
    <span class="cm-property">"created_time"</span>: {
      <span class="cm-property">"on_or_before"</span>: <span class="cm-string">"2022-10-13"</span>
    }
  }
}
</div></code></pre>

> ## 🚧
>
> The `<span class="cm-s-neo" data-testid="SyntaxHighlighter">timestamp</span>` filter condition does not require a property name. The API throws an error if you provide one.

### 

ID

Use a timestamp filter condition to filter results based on the `<span class="cm-s-neo" data-testid="SyntaxHighlighter">unique_id</span>` value.


| Field                                                                                    | Type                                                                   | Description                                                                                                                                                                       | Example value                                                      |
| ---------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">does_not_equal</span>`           | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">number</span>` | The value to compare the unique\_id property value against.<br/><br/>Returns database entries where the unique\_id property value differs from the provided value.                | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">42</span>` |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">equals</span>`                   | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">number</span>` | The value to compare the unique\_id property value against.<br/><br/>Returns database entries where the unique\_id property value is the same as the provided value.              | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">42</span>` |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">greater_than</span>`             | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">number</span>` | The value to compare the unique\_id property value against.<br/><br/>Returns database entries where the unique\_id property value exceeds the provided value.                     | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">42</span>` |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">greater_than_or_equal_to</span>` | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">number</span>` | The value to compare the unique\_id property value against.<br/><br/>Returns database entries where the unique\_id property value is equal to or exceeds the provided value.      | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">42</span>` |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">less_than</span>`                | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">number</span>` | The value to compare the unique\_id property value against.<br/><br/>Returns database entries where the unique\_id property value is less than the provided value.                | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">42</span>` |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">less_than_or_equal_to</span>`    | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">number</span>` | The value to compare the unique\_id property value against.<br/><br/>Returns database entries where the unique\_id property value is equal to or is less than the provided value. | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">42</span>` |

Example ID filter condition

<pre><button aria-label="Copy Code" class="rdmd-code-copy fa"></button><code class="rdmd-code lang-json theme-light" data-lang="json" name="Example ID filter condition" tabindex="0"><div class="cm-s-neo" data-testid="SyntaxHighlighter">{
  <span class="cm-property">"filter"</span>: {
    <span class="cm-property">"and"</span>: [
      {
        <span class="cm-property">"property"</span>: <span class="cm-string">"ID"</span>,
        <span class="cm-property">"unique_id"</span>: {
          <span class="cm-property">"greater_than"</span>: <span class="cm-number">1</span>
        }
      },
      {
        <span class="cm-property">"property"</span>: <span class="cm-string">"ID"</span>,
        <span class="cm-property">"unique_id"</span>: {
          <span class="cm-property">"less_than"</span>: <span class="cm-number">3</span>
        }
      }
    ]
  }
}
</div></code></pre>

## 

Compound filter conditions

You can use a compound filter condition to limit the results of a database query based on multiple conditions. This mimics filter chaining in the Notion UI.

![1340](https://files.readme.io/14ec7e8-Untitled.png "Untitled.png")
An example filter chain in the Notion UI

The above filters in the Notion UI are equivalent to the following compound filter condition via the API:

JSON

<pre><button aria-label="Copy Code" class="rdmd-code-copy fa"></button><code class="rdmd-code lang-json theme-light" data-lang="json" name="" tabindex="0"><div class="cm-s-neo" data-testid="SyntaxHighlighter">{
  <span class="cm-property">"and"</span>: [
    {
      <span class="cm-property">"property"</span>: <span class="cm-string">"Done"</span>,
      <span class="cm-property">"checkbox"</span>: {
        <span class="cm-property">"equals"</span>: <span class="cm-atom">true</span>
      }
    }, 
    {
      <span class="cm-property">"or"</span>: [
        {
          <span class="cm-property">"property"</span>: <span class="cm-string">"Tags"</span>,
          <span class="cm-property">"contains"</span>: <span class="cm-string">"A"</span>
        },
        {
          <span class="cm-property">"property"</span>: <span class="cm-string">"Tags"</span>,
          <span class="cm-property">"contains"</span>: <span class="cm-string">"B"</span>
        }
      ]
    }
  ]
}
</div></code></pre>

A compound filter condition contains an `<span class="cm-s-neo" data-testid="SyntaxHighlighter">and</span>` or `<span class="cm-s-neo" data-testid="SyntaxHighlighter">or</span>` key with a value that is an array of filter objects or nested compound filter objects. Nesting is supported up to two levels deep.


| Field                                                               | Type                                                                  | Description                                                                                                                                                                                                                                            | Example value                |
| ------------------------------------------------------------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------- |
| `<span class="cm-s-neo" data-testid="SyntaxHighlighter">and</span>` | `<span class="cm-s-neo" data-testid="SyntaxHighlighter">array</span>` | An array of[filter](https://developers.notion.com/reference/post-database-query-filter#type-specific-filter-conditions) objects or compound filter conditions.<br/><br/>Returns database entries that match **all** of the provided filter conditions. | Refer to the examples below. |
| or                                                                  | array                                                                 | An array of[filter](https://developers.notion.com/reference/post-database-query-filter#type-specific-filter-conditions) objects or compound filter conditions.<br/><br/>Returns database entries that match **any** of the provided filter conditions  | Refer to the examples below. |

### 

Example compound filter conditions

Example compound filter condition for a checkbox and number property value

<pre><button aria-label="Copy Code" class="rdmd-code-copy fa"></button><code class="rdmd-code lang-json theme-light" data-lang="json" name="Example compound filter condition for a checkbox and number property value" tabindex="0"><div class="cm-s-neo" data-testid="SyntaxHighlighter">{
  <span class="cm-property">"filter"</span>: {
    <span class="cm-property">"and"</span>: [
      {
        <span class="cm-property">"property"</span>: <span class="cm-string">"Complete"</span>,
        <span class="cm-property">"checkbox"</span>: {
          <span class="cm-property">"equals"</span>: <span class="cm-atom">true</span>
        }
      },
      {
        <span class="cm-property">"property"</span>: <span class="cm-string">"Working days"</span>,
        <span class="cm-property">"number"</span>: {
          <span class="cm-property">"greater_than"</span>: <span class="cm-number">10</span>
        }
      }
    ]
  }
}
</div></code></pre>

Example nested filter condition

<pre><button aria-label="Copy Code" class="rdmd-code-copy fa"></button><code class="rdmd-code lang-json theme-light" data-lang="json" name="Example nested filter condition" tabindex="0"><div class="cm-s-neo" data-testid="SyntaxHighlighter">{
  <span class="cm-property">"filter"</span>: {
    <span class="cm-property">"or"</span>: [
      {
        <span class="cm-property">"property"</span>: <span class="cm-string">"Description"</span>,
        <span class="cm-property">"rich_text"</span>: {
          <span class="cm-property">"contains"</span>: <span class="cm-string">"2023"</span>
        }
      },
      {
        <span class="cm-property">"and"</span>: [
          {
            <span class="cm-property">"property"</span>: <span class="cm-string">"Department"</span>,
            <span class="cm-property">"select"</span>: {
              <span class="cm-property">"equals"</span>: <span class="cm-string">"Engineering"</span>
            }
          },
          {
            <span class="cm-property">"property"</span>: <span class="cm-string">"Priority goal"</span>,
            <span class="cm-property">"checkbox"</span>: {
              <span class="cm-property">"equals"</span>: <span class="cm-atom">true</span>
            }
          }
        ]
      }
    ]
  }
}</div></code></pre>
